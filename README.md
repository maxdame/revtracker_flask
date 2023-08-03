**Welcome to my Nucamp portfolio project!**

_*CRITQUE AND FEEDBACK IS ALWAYS WELCOMED*_

This application has been developed using Flask, backed by a Postgres database and utilizes SQLAlchemy for ORM. This application is designed for accountants to automate the revenue recognition process. In the world of accounting, revenue must be recognized in compliance with the ASC 606 framework provided by GAAP. There are five steps to determine the proper treatment of revenue:

        - Identify the customer contract
        - Identify the performance obligations
        - Determine the transaction price
        - Allocate the price to the performance obligations
        - Recognize revenue as performance obligations are satisfied

In the most basic example, imagine that you have signed up for an annual Adobe subscription that costs $120 each year and begins January, 1st. You might think that Adobe recognizes your $120 payment as revenue in the month that the deposit was made or on the date that the contract was signed however that is wrong! Since your subscription contract is for a full year, the $120 must be amortized over your contract's 12 month service period. This means that Adobe would actually need to recognize $10 each month from January through December.

On the accounting side of things, this deferral of revenue creates a liability on the balance sheet that must be reduced each month as contracted performance obiligations are satisfied. This process is executed on a monthly basis with journal entries to recognize revenue and decrease the deferred revenue liability. Let's see how this process looks in action...

        Annual Adobe Subscription Invoiced:
        DEBIT: Accounts Receivable: 120
        CREDIT: Deferred Revenue: 120

This entry increases accounts receivable, indicating the customer has a balance due, while also increasing the balance of deferred revenue, which is now $120. No revenue has been recognized yet. At the end of the month, an accountant will then make a journal entry to properly recognize only $10 of annual subscription's revenue.

        Monthly Revenue Journal Entry:
        DEBIT: Deferred Revenue: 10
        CREDIT: Subscription Revenue: 10

The deferred revenue liability has now been reduced by $10 resulting in a balance of $110 while $10 of subscription revenue has now been recognized. This process will continue until the contract's balance in deferred revenue is $0.

**So What's The Problem?**

On the surface, revenue recognition may appear straightforward, but the example given barely dives into its complexities. Consider scenarios where you're dealing with tens or hundreds of thousands of customers, with contracts that don't necessarily align to a neat 12 month timeframe or a clean $120 value. Or imagine contracts with step-up pricing, multiple products with different performance obligations and billing cadences.

While there are online revenue recognition solutions available, they often come with hefty price tags. Additionally, these tools often remain underutilized due to their intricate systems, leading to excess tech debt and a platform that no one fully understands. So in many situations, accountants use what they know best – cumbersome, clunky, slow Excel spreadsheets. However, managing these spreadsheets can be a tedoious, error-prone, and time-consuming task.

**What Does This App Solve?**

To prevent wasted money and time, this application aims to provide a cost-effective solution to automate the revenue recognition process, simplifying the task while maintaining accuracy and efficiency. This application can create and manage customer records, contracts, and transactions. A contract can contain multiple transactions, each with varying service periods and billing cadences. These details are then used to streamline the generation of a contract's invoices automatically. Accountants can then utilize the application to pull data for a particular month, helping them obtain the appropriate revenue by product to be recognized in their monthly journal entries.

The application currently lacks a front end but is in a working version. That being said, there are many more features and error checks to add. As the application's development progresses, I intend to incorporate the capability to reconcile the Deferred/Accrued Revenue account balances, generate reports on various revenue KPIs and integrate with Quickbooks Online. This would facilitate automatic invoice creation and the booking of monthly revenue journal entries, providing a comprehensive and efficient solution for revenue management.

**API Endpoints**

Customers

    Index - GET - {{ _.base_url }}/customers
    Show - GET - {{ _.base_url }}/customers/<customer_id>
    Create - POST - {{base_url}}/customers (JSON body)
    Delete - DELETE - {{base_url}}/customers/<customer_id>
    Update - PUT - {{base_url}}/customers/<customer_id> (JSON body)
    Contracts by Customer - GET - {{base_url}}/customers/<customer_id>/contracts
    Invoices by Customer - GET - {{base_url}}/customers/<customer_id>/invoices

Contracts

    Index - GET - {{ _.base_url }}/contracts
    Show - GET - {{ _.base_url }}/contracts/<contract_id>
    Create - POST - {{base_url}}/contracts (JSON body)
    Delete - DELETE - {{base_url}}/contracts/<contract_id>
    Update - PUT - {{base_url}}/contracts/<contract_id> (JSON body)
    Transactions by Contract - GET - {{base_url}}/contracts/<contract_id>/transactions
    Invoices by Contract - GET - {{base_url}}/contracts/<contract_id>/invoices

Transactions

    Index - GET - {{base_url}}/transactions
    Show - GET - {{ _.base_url }}/transactions/<txn_id>
    Create - POST - {{base_url}}/transactions (JSON body)
    Delete - DELETE - {{base_url}}/transactions/<txn_id>
    Update - PUT - {{base_url}}/transactions/<txn_id> (JSON body)
    Invoices by Transaction- GET - {{base_url}}/transactions/<txn_id>/invoices

Invoices

    Index - GET - {{base_url}}/invoices
    Show - GET - {{base_url}}/invoices/<invoice_id>
    Create - POST - {{base_url}}/invoices (JSON body)
    Delete - DELETE - {{base_url}}/invoices/<invoice_id>
    Update - PUT - {{base_url}}/invoices (JSON body)
    Transactions by Invoice - GET - {{base_url}}/invoices/<invoice_id>/transactions

Accountant Tools

    Revenue by Product by Date Range- GET - {{base_url}}/accountant-tools/revenue-by-product (JSON body)

**Database Structure**

Database Name:

    revtracker_flask

Tables:

customers

    id: Integer type, primary key
    name: String type (max length 128), unique and not nullable
    created_on: Date type, not nullable, with default value as the current date and time
    is_active: Boolean type, not nullable, with default value as True
    address_line_1: String type (max length 200), not nullable
    address_line_2: String type (max length 200)
    city: String type (max length 100), not nullable
    state: String type (max length 100), not nullable
    zip_code: String type (max length 20), not nullable
    country: String type (max length 100), not nullable

transactions

    id: Integer type, primary key
    product: Enum type (ProductType), not nullable
    value: Float type, not nullable
    start_date: Date type, not nullable
    end_date: Date type, not nullable
    billing_cadence: Enum type (BillingCadence), not nullable, with default value as BillingCadence.monthly
    contract_id: Integer type, foreign key referencing id in contracts table, not nullable, indexed

contracts

    id: Integer type, primary key
    start_date: Date type, not nullable
    end_date: Date type, not nullable
    value: Float type, not nullable
    status: Enum type (ContractStatus), not nullable, with default value as ContractStatus.draft
    created_on: Date type, not nullable, with default value as the current date and time
    customer_id: Integer type, foreign key referencing id in customers table, not nullable, indexed

invoices

    id: Integer type, primary key
    date: Date type, not nullable, with default value as the current date and time
    payment_terms: Enum type (PaymentTerms), not nullable, with default value as PaymentTerms.due_upon_receipt
    amount_due: Float type, not nullable
    customer_id: Integer type, foreign key referencing id in customers table, not nullable, indexed
    contract_id: Integer type, foreign key referencing id in contracts table, not nullable, indexed

invoices_transactions

    invoice_id: Integer type, foreign key referencing id in invoices table, primary key
    transaction_id: Integer type, foreign key referencing id in transactions table, primary key

Relationships:

    - One Customer can have many Contracts
    - One Contract can have many Transactions
    - One Invoice can have many Transactions, and one Transaction can have many Invoices (Many-to-Many relationship with invoices_transactions table)
    - One Customer can have many Invoices
    - One Contract can have many Invoices

**HOW TO SETUP**

1.  Open a Bash terminal and navigate any where you would like to clone the repository and enter the following git command:

        git clone https://github.com/maxdame/revtracker_flask.git

2.  Navigate into the repository:

        cd revtracker_flask

3.  Make sure Docker Desktop is running then execute the following command in the Bash terminal to create the docker containers, database tables and populate the tables with test data:

        winpty docker compose up -d && winpty docker exec -it $(docker ps -qf "name=web") flask db migrate && winpty docker exec -it $(docker ps -qf "name=web") flask db upgrade && winpty docker exec -it $(docker ps -qf "name=web") python customer_seed.py && winpty docker exec -it $(docker ps -qf "name=web") python invoice_seed.py

4.  In a browser, navigate to pgAdmin at the following address:

        http://localhost:5433/

5.  In pgAdmin, create a new server with the following credentials:

        General Tab:
            - Name: revtracker_flask
        Connection Tab:
            - Host: pg
            - Port: 5432
            - Username: postgres
            - Password: admin123

6.  In another browser tab, navigate to the default flask address:

        http://localhost:5000/

7.  If you wish to test the API endpoints, import the insomnia.json file into Insomnia.
