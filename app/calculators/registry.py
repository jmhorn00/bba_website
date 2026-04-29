CALCULATORS = [
    # Savings & Goals
    {
        'slug': 'savings-goal',
        'title': 'Savings Goal Calculator',
        'description': 'What will it take to reach your savings goal? Calculate the monthly contribution needed.',
        'category': 'savings',
    },
    {
        'slug': 'savings-value',
        'title': 'Savings Value Calculator',
        'description': 'How much will your savings be worth? Project the future value of your current savings.',
        'category': 'savings',
    },
    # Tax
    {
        'slug': 'tax-estimator',
        'title': 'Federal Tax Estimator',
        'description': 'Estimate your total federal tax based on filing status, income, deductions, and credits.',
        'category': 'tax',
    },
    {
        'slug': 'earned-income-credit',
        'title': 'Earned Income Credit Calculator',
        'description': 'Estimate your Earned Income Tax Credit (EITC) based on income and family size.',
        'category': 'tax',
    },
    {
        'slug': 'estate-tax',
        'title': 'Estate Tax Estimator',
        'description': 'Estimate your estate tax liability based on the gross estate value and applicable exemptions.',
        'category': 'tax',
    },
    {
        'slug': 'marginal-effective-tax',
        'title': 'Marginal & Effective Tax Rate',
        'description': 'Understand the difference between your marginal tax rate and effective (average) tax rate.',
        'category': 'tax',
    },
    # Payroll & Income
    {
        'slug': 'paycheck-hourly',
        'title': 'Hourly Paycheck Calculator',
        'description': 'Calculate your take-home pay from an hourly wage after taxes and deductions.',
        'category': 'payroll',
    },
    {
        'slug': 'dual-income',
        'title': 'Dual Income Calculator',
        'description': 'Analyze the financial impact of one vs. two household incomes after taxes and expenses.',
        'category': 'payroll',
    },
    # Retirement
    {
        'slug': '401k',
        'title': '401(k) Savings Calculator',
        'description': 'See why a 401(k) is a plan you cannot afford to pass up — including employer match.',
        'category': 'retirement',
    },
    {
        'slug': '401k-distribution',
        'title': '401(k) Distribution Options',
        'description': 'What to do with your 401(k) when you leave an employer? Compare your distribution options.',
        'category': 'retirement',
    },
    {
        'slug': 'rmd-beneficiary',
        'title': 'RMD Calculator (Beneficiary)',
        'description': 'Calculate Required Minimum Distributions as a beneficiary of an inherited retirement account.',
        'category': 'retirement',
    },
    {
        'slug': 'rmd-owner',
        'title': 'RMD Calculator (Account Owner)',
        'description': 'Calculate your Required Minimum Distribution as the account owner using IRS Uniform Lifetime Table.',
        'category': 'retirement',
    },
    {
        'slug': 'retirement-income',
        'title': 'Retirement Income Calculator',
        'description': 'How long will your retirement savings last? Plan for a sustainable retirement income.',
        'category': 'retirement',
    },
    # Investment
    {
        'slug': 'long-term-care',
        'title': 'Long-Term Care Calculator',
        'description': 'Estimate the potential cost of long-term care and how it may impact your financial plan.',
        'category': 'investment',
    },
    {
        'slug': 'annual-return',
        'title': 'Annual Return Calculator',
        'description': 'Calculate the annualized return on your investment over a specified time period.',
        'category': 'investment',
    },
    {
        'slug': 'stock-options',
        'title': 'Stock Option Calculator',
        'description': 'Project how much stock option grants could be worth at various stock price levels.',
        'category': 'investment',
    },
    {
        'slug': 'future-value',
        'title': 'Investment Future Value Calculator',
        'description': 'Calculate the future value of a lump-sum investment with compound interest.',
        'category': 'investment',
    },
    {
        'slug': 'investment-goal',
        'title': 'Investment Goal Tracker',
        'description': 'Is your investment plan on track to meet your goals? Check your progress here.',
        'category': 'investment',
    },
    {
        'slug': 'investment-property',
        'title': 'Investment Property Calculator',
        'description': 'Analyze the potential returns and cash flow of a rental property investment.',
        'category': 'investment',
    },
]

CALCULATOR_MAP = {c['slug']: c for c in CALCULATORS}
