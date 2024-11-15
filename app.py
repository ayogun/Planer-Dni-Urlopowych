from flask import Flask, render_template, request
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Define the holidays for 2025 in Poland
holidays = {
    "Nowy Rok": "2025-01-01",  # New Year's Day
    "Święto Trzech Króli": "2025-01-06",  # Epiphany
    "Wielkanoc": ["2025-04-20", "2025-04-21"],  # Easter Sunday and Easter Monday
    "Święto Pracy": "2025-05-01",  # Labor Day
    "Święto Konstytucji 3 Maja": "2025-05-03",  # Constitution Day
    "Zielone Świątki": "2025-06-08",  # Pentecost
    "Boże Ciało": "2025-06-19",  # Corpus Christi
    "Wniebowzięcie Najświętszej Maryi Panny": "2025-08-15",  # Assumption of Mary
    "Wszystkich Świętych": "2025-11-01",  # All Saints' Day
    "Święto Niepodległości": "2025-11-11",  # Independence Day
    "Boże Narodzenie": ["2025-12-25", "2025-12-26"],  # Christmas Day and Second Day of Christmas
}

# Example of how to print the holidays
for holiday, date in holidays.items():
    if isinstance(date, list):
        print(f"{holiday}: {', '.join(date)}")
    else:
        print(f"{holiday}: {date}")


def str_to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')

# Convert holiday dates to datetime objects
official_holidays = [str_to_date(date) for date_list in holidays.values()
                     for date in (date_list if isinstance(date_list, list) else [date_list])]


def find_efficient_leaves(max_leaves=26):
    all_holiday_dates = set()
    
    # Convert all holidays to datetime objects
    for holiday, dates in holidays.items():
        if isinstance(dates, list):
            for date in dates:
                all_holiday_dates.add(str_to_date(date))
        else:
            all_holiday_dates.add(str_to_date(dates))
    
    # Generate all possible leave opportunities with scoring
    potential_leaves = []
    sorted_dates = sorted(list(all_holiday_dates))
    
    # First, identify all holiday clusters (including weekends)
    clusters = []
    current_cluster = set()
    
    start_date = min(sorted_dates) - timedelta(days=10)
    end_date = max(sorted_dates) + timedelta(days=10)
    current = start_date
    
    # Build initial clusters including weekends
    while current <= end_date:
        is_off = False
        if current in all_holiday_dates or current.weekday() >= 5:
            is_off = True
            
        if is_off:
            current_cluster.add(current)
        elif current_cluster:
            clusters.append(current_cluster)
            current_cluster = set()
            
        current += timedelta(days=1)
    
    if current_cluster:
        clusters.append(current_cluster)
    
    # Find gaps between clusters that are worth bridging
    for i in range(len(clusters) - 1):
        cluster1 = max(clusters[i])
        cluster2 = min(clusters[i + 1])
        gap_days = (cluster2 - cluster1).days - 1
        working_days = sum(1 for d in range(1, gap_days + 1) 
                         if (cluster1 + timedelta(days=d)).weekday() < 5)
        
        # More aggressive bridging - consider gaps up to 7 working days
        if working_days <= 7:  
            current = cluster1 + timedelta(days=1)
            while current < cluster2:
                if current.weekday() < 5 and current not in all_holiday_dates:
                    # Score based on potential for long stretches
                    score = 15 - working_days  # Higher score for smaller gaps
                    
                    # Bonus points for creating longer consecutive periods
                    days_before = sum(1 for d in clusters[i] if d >= current - timedelta(days=7))
                    days_after = sum(1 for d in clusters[i+1] if d <= current + timedelta(days=7))
                    
                    if days_before + days_after >= 7:  # If potential for week+ stretch
                        score += 5
                    if days_before + days_after >= 10:  # If potential for 10+ days
                        score += 5
                    
                    potential_leaves.append((current, score))
                current += timedelta(days=1)
    
    # Sort by score (higher is better) and select best days
    potential_leaves.sort(key=lambda x: (-x[1], x[0]))
    proposed_leaves = []
    leaves_count = 0
    
    # Take days that create longest stretches first
    for date, _ in potential_leaves:
        if leaves_count >= max_leaves:
            break
        if date not in proposed_leaves:
            proposed_leaves.append(date)
            leaves_count += 1
    
    return sorted(proposed_leaves)

def calculate_consecutive_days(proposed_leaves, all_holidays):
    consecutive_periods = []
    current_period = []
    
    #
    # Combine all dates including weekends
    all_dates = set()
    
    # Add all holidays and proposed leaves
    all_dates.update(proposed_leaves)
    all_dates.update(all_holidays)
    
    # Add all weekends between min and max dates
    if all_dates:
        start_date = min(all_dates) - timedelta(days=7)  # Look back one week
        end_date = max(all_dates) + timedelta(days=7)    # Look ahead one week
        current = start_date
        
        while current <= end_date:
            if current.weekday() >= 5:  # Saturday or Sunday
                all_dates.add(current)
            current += timedelta(days=1)
    
    # Sort all dates
    all_dates = sorted(list(all_dates))
    
    # Find consecutive periods
    for date in all_dates:
        if not current_period:
            current_period = [date]
        else:
            prev_date = current_period[-1]
            if (date - prev_date).days == 1:
                current_period.append(date)
            else:
                if len(current_period) >= 3:  # Only keep periods of 3+ days
                    consecutive_periods.append(current_period)
                current_period = [date]
    
    if current_period and len(current_period) >= 3:
        consecutive_periods.append(current_period)
    
    return consecutive_periods

@app.route('/', methods=['GET', 'POST'])
def index():
    proposed_leaves = []
    consecutive_periods = []
    total_consecutive_days = 0
    total_holidays = 0

    if request.method == 'POST':
        try:
            max_leaves = int(request.form['max_leaves'].strip() or "26")
        except ValueError:
            max_leaves = 26
        
        proposed_leaves = find_efficient_leaves(max_leaves)
        
        all_holidays = [str_to_date(date) for holiday in holidays.values() 
                        for date in (holiday if isinstance(holiday, list) else [holiday])]
        
        # Calculate all off days
        all_off_days = set()
        
        # Add all weekends in 2025
        current = datetime(2025, 1, 1)
        end = datetime(2025, 12, 31)
        while current <= end:
            if current.weekday() >= 5:  # Saturday or Sunday
                all_off_days.add(current)
            current += timedelta(days=1)
        
        # Add official holidays and proposed leaves
        all_off_days.update(all_holidays)
        all_off_days.update(proposed_leaves)
        
        consecutive_periods = calculate_consecutive_days(proposed_leaves, all_holidays)
        
        # Calculate total consecutive days
        for period in consecutive_periods:
            total_consecutive_days += len(period)
        
        total_holidays = len(all_off_days)



    return render_template('index.html', proposed_leaves=proposed_leaves, 
                           consecutive_periods=consecutive_periods, 
                           total_consecutive_days=total_consecutive_days,
                           total_holidays=total_holidays,
                           official_holidays=official_holidays, 
                           datetime=datetime)  # Pass datetime to the template

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
