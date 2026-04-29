"""Server-side calculation logic for all financial calculators."""

from decimal import Decimal, ROUND_HALF_UP


def fmt(value):
    """Format a number as currency string."""
    try:
        return f'${float(value):,.2f}'
    except (TypeError, ValueError):
        return '$0.00'


def fmt_pct(value):
    return f'{float(value):.2f}%'


# ─── Tax brackets 2024 ────────────────────────────────────────────────────────
TAX_BRACKETS_2024 = {
    'single': [
        (11_600, 0.10), (47_150, 0.12), (100_525, 0.22),
        (191_950, 0.24), (243_725, 0.32), (609_350, 0.35), (float('inf'), 0.37),
    ],
    'married_filing_jointly': [
        (23_200, 0.10), (94_300, 0.12), (201_050, 0.22),
        (383_900, 0.24), (487_450, 0.32), (731_200, 0.35), (float('inf'), 0.37),
    ],
    'married_filing_separately': [
        (11_600, 0.10), (47_150, 0.12), (100_525, 0.22),
        (191_950, 0.24), (243_725, 0.32), (365_600, 0.35), (float('inf'), 0.37),
    ],
    'head_of_household': [
        (16_550, 0.10), (63_100, 0.12), (100_500, 0.22),
        (191_950, 0.24), (243_700, 0.32), (609_350, 0.35), (float('inf'), 0.37),
    ],
}

STANDARD_DEDUCTIONS_2024 = {
    'single': 14_600,
    'married_filing_jointly': 29_200,
    'married_filing_separately': 14_600,
    'head_of_household': 21_900,
}

# IRS Uniform Lifetime Table (age -> factor)
UNIFORM_LIFETIME_TABLE = {
    72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9,
    78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7,
    84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9,
    90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9,
    96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4,
}


def calc_tax(taxable_income, filing_status):
    brackets = TAX_BRACKETS_2024.get(filing_status, TAX_BRACKETS_2024['single'])
    tax = 0.0
    prev = 0.0
    for limit, rate in brackets:
        if taxable_income <= prev:
            break
        taxable_at_rate = min(taxable_income, limit) - prev
        tax += taxable_at_rate * rate
        prev = limit
    return tax


# ─── Calculator functions ─────────────────────────────────────────────────────

def savings_goal(post):
    try:
        goal = float(post.get('goal', 0))
        annual_rate = float(post.get('annual_rate', 6)) / 100
        years = int(post.get('years', 10))
        current = float(post.get('current_savings', 0))

        r = annual_rate / 12
        n = years * 12

        # Future value of current savings
        fv_current = current * (1 + r) ** n
        remaining = max(0, goal - fv_current)

        # Monthly savings needed for remaining
        if r == 0:
            monthly = remaining / n if n > 0 else 0
        else:
            monthly = remaining * r / ((1 + r) ** n - 1)

        return {
            'goal': fmt(goal),
            'monthly_needed': fmt(monthly),
            'years': years,
            'fv_current': fmt(fv_current),
            'total_contributions': fmt(monthly * n),
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def savings_value(post):
    try:
        monthly = float(post.get('monthly_savings', 0))
        annual_rate = float(post.get('annual_rate', 6)) / 100
        years = int(post.get('years', 10))
        current = float(post.get('current_savings', 0))

        r = annual_rate / 12
        n = years * 12

        fv_current = current * (1 + r) ** n
        if r == 0:
            fv_contributions = monthly * n
        else:
            fv_contributions = monthly * ((1 + r) ** n - 1) / r

        total = fv_current + fv_contributions
        return {
            'future_value': fmt(total),
            'total_contributed': fmt(monthly * n + current),
            'total_interest': fmt(total - monthly * n - current),
            'years': years,
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def tax_estimator(post):
    try:
        filing_status = post.get('filing_status', 'single')
        gross_income = float(post.get('gross_income', 0))
        other_income = float(post.get('other_income', 0))
        deductions = float(post.get('deductions', 0))
        credits = float(post.get('credits', 0))
        withholding = float(post.get('withholding', 0))

        std = STANDARD_DEDUCTIONS_2024.get(filing_status, 14_600)
        total_income = gross_income + other_income
        itemized = deductions if deductions > std else std
        taxable = max(0, total_income - itemized)

        tax = calc_tax(taxable, filing_status)
        after_credits = max(0, tax - credits)
        refund_owed = withholding - after_credits
        effective = (after_credits / total_income * 100) if total_income > 0 else 0
        marginal = 0
        prev = 0
        brackets = TAX_BRACKETS_2024.get(filing_status, TAX_BRACKETS_2024['single'])
        for limit, rate in brackets:
            if taxable <= limit:
                marginal = rate * 100
                break
            prev = limit

        return {
            'total_income': fmt(total_income),
            'deduction_used': fmt(itemized),
            'taxable_income': fmt(taxable),
            'estimated_tax': fmt(after_credits),
            'effective_rate': fmt_pct(effective),
            'marginal_rate': fmt_pct(marginal),
            'refund_or_owed': fmt(abs(refund_owed)),
            'refund_owed_label': 'Estimated Refund' if refund_owed >= 0 else 'Amount Owed',
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def earned_income_credit(post):
    try:
        income = float(post.get('income', 0))
        children = int(post.get('children', 0))
        filing_status = post.get('filing_status', 'single')

        # 2024 EITC max credit amounts (approximate)
        max_credits = {0: 632, 1: 4_213, 2: 6_960, 3: 7_830}
        phase_out_mfj = {0: 25_511, 1: 53_120, 2: 59_478, 3: 63_398}
        phase_out_single = {0: 18_591, 1: 49_084, 2: 55_768, 3: 59_899}

        kids = min(children, 3)
        phase_out = phase_out_mfj[kids] if 'jointly' in filing_status else phase_out_single[kids]
        max_credit = max_credits[kids]

        if income > phase_out or income <= 0:
            credit = 0
        else:
            credit = max_credit * max(0, (phase_out - income) / phase_out)

        return {
            'estimated_credit': fmt(credit),
            'income': fmt(income),
            'children': children,
            'note': 'This is an estimate only. Actual credit depends on your complete tax situation.',
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def estate_tax(post):
    try:
        gross_estate = float(post.get('gross_estate', 0))
        debts = float(post.get('debts', 0))
        charitable = float(post.get('charitable', 0))
        marital_deduction = float(post.get('marital_deduction', 0))

        # 2024 federal exemption
        exemption = 13_610_000

        taxable_estate = max(0, gross_estate - debts - charitable - marital_deduction - exemption)
        tax = taxable_estate * 0.40 if taxable_estate > 0 else 0

        return {
            'gross_estate': fmt(gross_estate),
            'taxable_estate': fmt(taxable_estate),
            'estimated_tax': fmt(tax),
            'exemption_used': fmt(min(gross_estate, exemption)),
            'note': '2024 federal estate tax exemption: $13,610,000 per person.',
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def marginal_effective_tax(post):
    try:
        income = float(post.get('income', 0))
        filing_status = post.get('filing_status', 'single')
        std = STANDARD_DEDUCTIONS_2024.get(filing_status, 14_600)
        taxable = max(0, income - std)

        tax = calc_tax(taxable, filing_status)
        effective = (tax / income * 100) if income > 0 else 0

        marginal = 0
        brackets = TAX_BRACKETS_2024.get(filing_status, TAX_BRACKETS_2024['single'])
        for limit, rate in brackets:
            if taxable <= limit:
                marginal = rate * 100
                break

        return {
            'gross_income': fmt(income),
            'taxable_income': fmt(taxable),
            'total_tax': fmt(tax),
            'effective_rate': fmt_pct(effective),
            'marginal_rate': fmt_pct(marginal),
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def paycheck_hourly(post):
    try:
        hourly = float(post.get('hourly_rate', 0))
        hours = float(post.get('hours_per_week', 40))
        filing_status = post.get('filing_status', 'single')

        gross_weekly = hourly * hours
        gross_annual = gross_weekly * 52

        std = STANDARD_DEDUCTIONS_2024.get(filing_status, 14_600)
        taxable = max(0, gross_annual - std)
        annual_tax = calc_tax(taxable, filing_status)

        fica = gross_annual * 0.0765  # Social Security + Medicare
        weekly_tax = annual_tax / 52
        weekly_fica = fica / 52
        net_weekly = gross_weekly - weekly_tax - weekly_fica

        return {
            'hourly_rate': fmt(hourly),
            'hours_per_week': hours,
            'gross_weekly': fmt(gross_weekly),
            'gross_annual': fmt(gross_annual),
            'federal_tax_weekly': fmt(weekly_tax),
            'fica_weekly': fmt(weekly_fica),
            'net_weekly': fmt(net_weekly),
            'net_annual': fmt(net_weekly * 52),
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def dual_income(post):
    try:
        income1 = float(post.get('income1', 0))
        income2 = float(post.get('income2', 0))
        work_expenses = float(post.get('work_expenses', 0))  # childcare, commute, etc.

        # Single income (MFJ)
        std_mfj = 29_200
        taxable_single = max(0, income1 - std_mfj)
        tax_single = calc_tax(taxable_single, 'married_filing_jointly')

        # Dual income (MFJ combined)
        combined = income1 + income2
        taxable_dual = max(0, combined - std_mfj)
        tax_dual = calc_tax(taxable_dual, 'married_filing_jointly')

        additional_tax = tax_dual - tax_single
        net_second_income = income2 - additional_tax - work_expenses

        return {
            'income1': fmt(income1),
            'income2': fmt(income2),
            'combined_gross': fmt(combined),
            'single_tax': fmt(tax_single),
            'dual_tax': fmt(tax_dual),
            'additional_tax': fmt(additional_tax),
            'work_expenses': fmt(work_expenses),
            'net_second_income': fmt(net_second_income),
            'breakeven': 'positive' if net_second_income > 0 else 'negative',
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def calc_401k(post):
    try:
        salary = float(post.get('salary', 0))
        contrib_pct = float(post.get('contrib_pct', 6)) / 100
        employer_match_pct = float(post.get('employer_match_pct', 3)) / 100
        annual_return = float(post.get('annual_return', 7)) / 100
        years = int(post.get('years', 30))

        annual_contrib = salary * contrib_pct
        employer_contrib = salary * employer_match_pct
        total_annual = annual_contrib + employer_contrib

        r = annual_return / 12
        n = years * 12
        monthly = total_annual / 12

        if r == 0:
            fv = monthly * n
        else:
            fv = monthly * ((1 + r) ** n - 1) / r

        total_contributed = total_annual * years
        tax_savings = annual_contrib * 0.22 * years  # assuming 22% bracket

        return {
            'annual_contribution': fmt(annual_contrib),
            'employer_contribution': fmt(employer_contrib),
            'total_annual': fmt(total_annual),
            'future_value': fmt(fv),
            'total_contributed': fmt(total_contributed),
            'investment_growth': fmt(fv - total_contributed),
            'estimated_tax_savings': fmt(tax_savings),
            'years': years,
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def calc_401k_distribution(post):
    try:
        balance = float(post.get('balance', 0))
        age = int(post.get('age', 55))
        tax_rate = float(post.get('tax_rate', 22)) / 100

        lump_sum_tax = balance * tax_rate
        penalty = balance * 0.10 if age < 59.5 else 0
        lump_sum_net = balance - lump_sum_tax - penalty

        # Rollover keeps full balance growing
        rollover_years = max(65 - age, 5)
        r = 0.07
        rollover_fv = balance * (1 + r) ** rollover_years

        return {
            'balance': fmt(balance),
            'lump_sum_tax': fmt(lump_sum_tax),
            'early_withdrawal_penalty': fmt(penalty),
            'lump_sum_net': fmt(lump_sum_net),
            'rollover_balance': fmt(balance),
            'rollover_fv': fmt(rollover_fv),
            'rollover_years': rollover_years,
            'penalty_applies': age < 59.5,
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def rmd_beneficiary(post):
    try:
        balance = float(post.get('balance', 0))
        age = int(post.get('age', 72))

        factor = UNIFORM_LIFETIME_TABLE.get(age)
        if not factor:
            if age < 72:
                return {'error': 'RMDs typically begin at age 73 (born after 1950). Please enter age 72+.'}
            factor = max(1.0, 6.4 - (age - 100) * 0.5)

        rmd = balance / factor
        return {
            'account_balance': fmt(balance),
            'age': age,
            'life_expectancy_factor': factor,
            'annual_rmd': fmt(rmd),
            'monthly_rmd': fmt(rmd / 12),
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def rmd_owner(post):
    return rmd_beneficiary(post)


def retirement_income(post):
    try:
        balance = float(post.get('balance', 0))
        monthly_withdrawal = float(post.get('monthly_withdrawal', 2000))
        annual_return = float(post.get('annual_return', 5)) / 100
        monthly_ss = float(post.get('monthly_ss', 0))

        r = annual_return / 12
        net_monthly = max(0, monthly_withdrawal - monthly_ss)

        if net_monthly <= 0:
            return {'error': 'Social Security income covers all withdrawals — savings will grow indefinitely.'}

        if r == 0:
            months = balance / net_monthly if net_monthly > 0 else 0
        else:
            if r >= net_monthly / balance:
                months = float('inf')
            else:
                months = -1 * (1 / r) * (1 - balance * r / net_monthly) if net_monthly > balance * r else float('inf')
                # Standard formula: n = -ln(1 - P*r/PMT) / ln(1+r)
                import math
                ratio = balance * r / net_monthly
                if ratio >= 1:
                    months = float('inf')
                else:
                    months = -math.log(1 - ratio) / math.log(1 + r)

        if months == float('inf'):
            years_label = 'Your savings will not be depleted (returns exceed withdrawals)'
        else:
            years = months / 12
            years_label = f'{years:.1f} years ({int(months)} months)'

        return {
            'balance': fmt(balance),
            'monthly_withdrawal': fmt(monthly_withdrawal),
            'monthly_ss': fmt(monthly_ss),
            'net_monthly_from_savings': fmt(net_monthly),
            'duration': years_label,
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def long_term_care(post):
    try:
        daily_rate = float(post.get('daily_rate', 350))
        years_care = float(post.get('years_care', 3))
        inflation_rate = float(post.get('inflation_rate', 3)) / 100
        years_until = int(post.get('years_until', 20))

        current_annual = daily_rate * 365
        future_annual = current_annual * (1 + inflation_rate) ** years_until
        total_cost = future_annual * years_care

        return {
            'current_annual_cost': fmt(current_annual),
            'future_annual_cost': fmt(future_annual),
            'years_until': years_until,
            'years_care': years_care,
            'total_estimated_cost': fmt(total_cost),
            'inflation_rate': fmt_pct(inflation_rate * 100),
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def annual_return(post):
    try:
        beginning = float(post.get('beginning_value', 0))
        ending = float(post.get('ending_value', 0))
        years = float(post.get('years', 1))
        dividends = float(post.get('dividends', 0))

        if beginning <= 0:
            return {'error': 'Beginning value must be greater than zero.'}

        total_return_pct = ((ending + dividends - beginning) / beginning) * 100
        annualized = ((ending + dividends) / beginning) ** (1 / years) - 1

        return {
            'beginning_value': fmt(beginning),
            'ending_value': fmt(ending),
            'total_dividends': fmt(dividends),
            'total_gain_loss': fmt(ending + dividends - beginning),
            'total_return': fmt_pct(total_return_pct),
            'annualized_return': fmt_pct(annualized * 100),
            'years': years,
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def stock_options(post):
    try:
        shares = int(post.get('shares', 0))
        grant_price = float(post.get('grant_price', 0))
        current_price = float(post.get('current_price', 0))
        target_price = float(post.get('target_price', 0))
        tax_rate = float(post.get('tax_rate', 22)) / 100

        current_value = shares * (current_price - grant_price) if current_price > grant_price else 0
        target_value = shares * (target_price - grant_price) if target_price > grant_price else 0

        current_after_tax = current_value * (1 - tax_rate)
        target_after_tax = target_value * (1 - tax_rate)

        return {
            'shares': shares,
            'grant_price': fmt(grant_price),
            'current_price': fmt(current_price),
            'target_price': fmt(target_price),
            'current_spread': fmt(current_value),
            'current_after_tax': fmt(current_after_tax),
            'target_spread': fmt(target_value),
            'target_after_tax': fmt(target_after_tax),
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def future_value(post):
    try:
        principal = float(post.get('principal', 0))
        annual_rate = float(post.get('annual_rate', 7)) / 100
        years = int(post.get('years', 10))
        monthly_addition = float(post.get('monthly_addition', 0))
        compounds = int(post.get('compounds', 12))  # per year

        r = annual_rate / compounds
        n = compounds * years

        fv_principal = principal * (1 + r) ** n

        if monthly_addition > 0:
            period_addition = monthly_addition * (12 / compounds)
            if r == 0:
                fv_additions = period_addition * n
            else:
                fv_additions = period_addition * ((1 + r) ** n - 1) / r
        else:
            fv_additions = 0

        total = fv_principal + fv_additions
        total_invested = principal + monthly_addition * 12 * years

        return {
            'principal': fmt(principal),
            'future_value': fmt(total),
            'total_invested': fmt(total_invested),
            'total_interest': fmt(total - total_invested),
            'years': years,
            'annual_rate': fmt_pct(annual_rate * 100),
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def investment_goal(post):
    try:
        current_value = float(post.get('current_value', 0))
        goal = float(post.get('goal', 0))
        annual_return_rate = float(post.get('annual_return', 7)) / 100
        years = int(post.get('years', 10))
        monthly_addition = float(post.get('monthly_addition', 0))

        r = annual_return_rate / 12
        n = years * 12

        fv_current = current_value * (1 + r) ** n
        if r == 0:
            fv_additions = monthly_addition * n
        else:
            fv_additions = monthly_addition * ((1 + r) ** n - 1) / r

        projected = fv_current + fv_additions
        gap = goal - projected
        on_track = projected >= goal

        # Monthly needed to hit goal
        remaining = max(0, goal - fv_current)
        if r == 0:
            monthly_needed = remaining / n if n > 0 else 0
        else:
            monthly_needed = remaining * r / ((1 + r) ** n - 1)

        return {
            'current_value': fmt(current_value),
            'goal': fmt(goal),
            'projected_value': fmt(projected),
            'gap': fmt(abs(gap)),
            'on_track': on_track,
            'monthly_needed': fmt(monthly_needed),
            'years': years,
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


def investment_property(post):
    try:
        purchase_price = float(post.get('purchase_price', 0))
        down_payment_pct = float(post.get('down_payment_pct', 20)) / 100
        interest_rate = float(post.get('interest_rate', 7)) / 100
        loan_years = int(post.get('loan_years', 30))
        monthly_rent = float(post.get('monthly_rent', 0))
        monthly_expenses = float(post.get('monthly_expenses', 0))
        appreciation_rate = float(post.get('appreciation_rate', 3)) / 100
        hold_years = int(post.get('hold_years', 10))

        down_payment = purchase_price * down_payment_pct
        loan_amount = purchase_price - down_payment

        # Monthly mortgage payment
        r = interest_rate / 12
        n = loan_years * 12
        if r == 0:
            monthly_mortgage = loan_amount / n
        else:
            monthly_mortgage = loan_amount * r * (1 + r) ** n / ((1 + r) ** n - 1)

        monthly_cash_flow = monthly_rent - monthly_expenses - monthly_mortgage
        annual_cash_flow = monthly_cash_flow * 12

        # Cap rate
        noi = (monthly_rent - monthly_expenses) * 12
        cap_rate = (noi / purchase_price * 100) if purchase_price > 0 else 0

        # Future property value
        future_value_prop = purchase_price * (1 + appreciation_rate) ** hold_years

        return {
            'purchase_price': fmt(purchase_price),
            'down_payment': fmt(down_payment),
            'loan_amount': fmt(loan_amount),
            'monthly_mortgage': fmt(monthly_mortgage),
            'monthly_cash_flow': fmt(monthly_cash_flow),
            'annual_cash_flow': fmt(annual_cash_flow),
            'cap_rate': fmt_pct(cap_rate),
            'future_value': fmt(future_value_prop),
            'hold_years': hold_years,
            'cash_flow_positive': monthly_cash_flow >= 0,
        }
    except (ValueError, ZeroDivisionError):
        return {'error': 'Please check your inputs and try again.'}


# Dispatch table
CALC_FUNCTIONS = {
    'savings-goal': savings_goal,
    'savings-value': savings_value,
    'tax-estimator': tax_estimator,
    'earned-income-credit': earned_income_credit,
    'estate-tax': estate_tax,
    'marginal-effective-tax': marginal_effective_tax,
    'paycheck-hourly': paycheck_hourly,
    'dual-income': dual_income,
    '401k': calc_401k,
    '401k-distribution': calc_401k_distribution,
    'rmd-beneficiary': rmd_beneficiary,
    'rmd-owner': rmd_owner,
    'retirement-income': retirement_income,
    'long-term-care': long_term_care,
    'annual-return': annual_return,
    'stock-options': stock_options,
    'future-value': future_value,
    'investment-goal': investment_goal,
    'investment-property': investment_property,
}
