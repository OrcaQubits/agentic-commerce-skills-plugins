---
name: spree-testing
description: >
  Test Spree applications and extensions with RSpec — `spree_dev_tools` gem
  (v5.2+) for factories and helpers, FactoryBot patterns (prefer `build` over
  `create`), Capybara feature specs, controller/request specs, testing
  decorators and subscribers, dummy app for extension testing, system specs for
  the Hotwire admin, and CI patterns. Use when writing Spree tests, setting up
  CI, or refactoring slow specs.
---

# Spree Testing

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/tutorial/testing for the canonical testing tutorial.
2. Check the `spree_dev_tools` gem on RubyGems and GitHub for the current factory inventory and helpers.
3. Inspect the Spree gem's own `spec/` directory for the latest test patterns.
4. Cross-reference Rails 7+ testing docs for current request/system spec patterns.
5. For RSpec, FactoryBot, Capybara — check current gem versions vs your Spree's Gemfile.lock.

## Conceptual Architecture

### The Testing Stack

| Tool | Purpose |
|------|---------|
| **RSpec** | Test framework |
| **FactoryBot** | Test data factories |
| **Capybara** | Feature/system specs (browser-driven) |
| **`spree_dev_tools`** (v5.2+) | Spree-specific factories, shared examples, helpers |
| **Selenium / Cuprite** | Headless browser for system specs |
| **Sidekiq Testing** | Background job assertions |
| **VCR / WebMock** | Stub external APIs |

### `spree_dev_tools` (v5.2+)

Formally introduced in v5.2 as a separate gem (was previously bundled). Provides:
- Pre-built factories for every Spree model (`Spree::Order`, `Spree::Product`, `Spree::User`, etc.)
- Shared examples for common test patterns
- Helpers for creating realistic test scenarios (`create_order_with_two_items`, etc.)
- Engine spec setup for extension testing

```ruby
# Gemfile
group :development, :test do
  gem 'spree_dev_tools'
end
```

### Spec Types

| Type | What it tests |
|------|---------------|
| **Model spec** | A model's methods, validations, associations |
| **Request spec** | HTTP request → response, including auth |
| **Controller spec** | (Legacy — Rails 5+ prefers request specs) |
| **Feature spec** | User behavior via Capybara |
| **System spec** | Like feature but with full Rails 5.1+ integration |
| **Job spec** | Background job logic |
| **Mailer spec** | Email content |
| **Subscriber spec** | Event subscriber assertions |

### `build` vs `create`

```ruby
# Slow — hits the database
let(:product) { create(:product) }

# Fast — in-memory only
let(:product) { build(:product) }

# Stub — fastest, no validation
let(:product) { build_stubbed(:product) }
```

Use `build` when you only need the object to call methods. Reach for `create` only when you need persistence (`find_by`, foreign keys, callbacks that hit the DB).

### Common Factories

```ruby
create(:product)                     # basic product
create(:product, name: 'Foo')        # with overrides
create(:product_in_stock)            # has stock
create(:order_with_line_items, line_items_count: 3)
create(:order_ready_to_complete)
create(:completed_order_with_pending_payment)
create(:user_with_addresses)
create(:admin_user)                   # has admin role
```

Verify the actual factory names against the `spree_dev_tools` source.

### Testing a Decorator

```ruby
# spec/models/spree/product_decorator_spec.rb
require 'rails_helper'

RSpec.describe Spree::Product, type: :model do
  describe 'editor_pick scope' do
    let!(:pick) { create(:product, editor_pick: true) }
    let!(:other) { create(:product, editor_pick: false) }

    it 'returns only editor-picked products' do
      expect(Spree::Product.editor_picks).to contain_exactly(pick)
    end
  end

  describe '#display_name' do
    let(:product) { build(:product, seo_title: 'Premium Tee', name: 'Tee') }

    it 'prefers seo_title' do
      expect(product.display_name).to eq('Premium Tee')
    end
  end
end
```

### Testing a Subscriber

```ruby
# spec/subscribers/order_completed_subscriber_spec.rb
require 'rails_helper'

RSpec.describe OrderCompletedSubscriber do
  let(:order) { create(:order, state: 'complete') }

  it 'enqueues an accounting sync' do
    expect {
      Spree::Bus.publish('order.completed', order: order, user: order.user)
    }.to have_enqueued_job(AccountingSyncJob).with(order_id: order.id)
  end
end
```

### Testing a Service / Dependency Override

```ruby
RSpec.describe MyApp::CartAddItemService do
  let(:order)   { create(:order) }
  let(:variant) { create(:variant) }

  it 'adds an item with extra metadata' do
    service = described_class.new
    result = service.call(order: order, variant: variant, quantity: 1, options: { source: 'app' })

    expect(result).to be_a(Spree::LineItem)
    expect(result.metafields.find_by(key: 'source').value).to eq('app')
  end
end
```

### Feature/System Specs (Hotwire-aware)

Spree v5 admin uses Hotwire/Turbo. System specs need a JS driver:

```ruby
# spec/system/admin/products_spec.rb
require 'rails_helper'

RSpec.describe 'Admin products', type: :system do
  let(:admin) { create(:admin_user) }
  before { sign_in admin; driven_by(:cuprite) }   # or :selenium_chrome_headless

  it 'creates a product' do
    visit spree.admin_products_path
    click_on 'New Product'
    fill_in 'Name', with: 'Test Product'
    fill_in 'Price', with: '19.99'
    click_on 'Create'
    expect(page).to have_content('Test Product')
  end
end
```

### Testing API v3 Endpoints

```ruby
RSpec.describe 'Store API v3 products', type: :request do
  let(:store) { create(:store) }
  let(:api_key) { create(:publishable_api_key, store: store).key }
  let!(:product) { create(:product, stores: [store]) }

  it 'lists products' do
    get '/api/v3/store/products', headers: { 'Authorization' => "Bearer #{api_key}" }
    expect(response).to have_http_status(:ok)
    body = JSON.parse(response.body)
    expect(body['data'].first['id']).to start_with('prod_')
    expect(body['data'].first['name']).to eq(product.name)
  end
end
```

(Verify the factory name `:publishable_api_key` in current `spree_dev_tools`.)

### Testing With Sidekiq

```ruby
# config/initializers/sidekiq.rb in test env auto-uses InlineTesting
require 'sidekiq/testing'
Sidekiq::Testing.fake!   # default for specs

RSpec.describe 'webhook delivery' do
  it 'enqueues a delivery job on order.completed' do
    order = create(:order, state: 'complete')
    expect {
      Spree::Bus.publish('order.completed', order: order)
    }.to change(Spree::WebhookDeliveryJob.jobs, :size).by(1)
  end
end
```

(Verify the job class name in the current Webhooks 2.0 implementation.)

### Testing an Extension's Engine

Extensions test against a dummy Rails app:

```bash
cd spree_my_extension
bundle exec rake test_app  # generates spec/dummy
bundle exec rspec
```

The `test_app` rake task (verify it exists in current scaffolding) creates `spec/dummy` mounting Spree + your extension. Specs run against it.

### Mocking External APIs

```ruby
# spec/requests/stripe_webhook_spec.rb
RSpec.describe 'Stripe webhook', type: :request do
  it 'processes payment_intent.succeeded' do
    stub_request(:get, %r{api\.stripe\.com/v1/payment_intents})
      .to_return(body: { id: 'pi_…', status: 'succeeded' }.to_json)
    # ...
  end
end
```

WebMock is the standard; VCR is heavier-handed (records real responses to replay).

## Implementation Guidance

### Spec Suite Setup

```ruby
# spec/rails_helper.rb
require 'spec_helper'
ENV['RAILS_ENV'] ||= 'test'
require_relative '../config/environment'
require 'rspec/rails'
require 'capybara/rspec'
require 'sidekiq/testing'

Dir[Rails.root.join('spec/support/**/*.rb')].sort.each { |f| require f }

RSpec.configure do |config|
  config.use_transactional_fixtures = true
  config.infer_spec_type_from_file_location!
  config.filter_rails_from_backtrace!

  config.include FactoryBot::Syntax::Methods
  config.include Spree::TestingSupport::AuthorizationHelpers, type: :controller
  config.include Spree::TestingSupport::ControllerRequests, type: :controller
  config.include Spree::TestingSupport::Capybara, type: :feature
end
```

(Verify the exact testing-support modules — they evolve.)

### Speed Strategies

1. **Prefer `build` and `build_stubbed`** over `create`
2. **Don't load full Rails for unit-y specs** when possible
3. **Parallel test execution** — `parallel_tests` gem with N processes
4. **Skip image processing in tests** — `Spree::Config.image_processor = :stub` (verify config name)
5. **Limit `js: true`** to specs that genuinely need a browser
6. **Mock external HTTP** — every real request is a slow test

### CI Patterns

```yaml
# .github/workflows/ci.yml (sketch)
jobs:
  rspec:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
      - run: bundle install --jobs 4
      - run: bin/rails db:create db:migrate
      - run: bundle exec rspec --format progress
```

### Common Pitfalls

- **Using `create` everywhere** — specs take 10x longer than necessary.
- **Forgetting `Sidekiq::Testing.fake!`** — jobs fire synchronously and pollute specs.
- **System specs without `driven_by(:cuprite)` or similar** — Turbo events don't fire.
- **Stubbing `Spree::Order#total`** — breaks downstream service-object behavior; create the right line items instead.
- **Not testing decorators with the real model loaded** — autoloading order matters.
- **Brittle Capybara selectors** — use semantic selectors (`data-test-id`) not classes.
- **Forgetting to seed default Store / Country / Zone** — `spree_dev_tools` provides setup helpers; use them.

Always cross-reference the current `spree_dev_tools` factories and the Spree gem's own `spec/` for the canonical patterns for the version you target.
