import csv
from datetime import datetime

portfolio = []

print("=" * 45)
print("     STOCK PORTFOLIO PERFORMANCE TRACKER")
print("=" * 45)

while True:
    ticker = input("\nEnter stock ticker (e.g. TCS): ").strip().upper()

    if not ticker:
        print("Ticker cannot be empty!")
        continue

    try:
        buy_price = float(input("Enter buying price per share: "))
        quantity = int(input("Enter number of shares: "))
        current_price = float(input("Enter current price per share: "))

        if buy_price <= 0 or current_price < 0 or quantity <= 0:
            print("Please enter valid positive values.")
            continue

    except ValueError:
        print("Invalid input! Enter numbers for prices and quantity.")
        continue

    invested = buy_price * quantity
    market_value = current_price * quantity
    profit_loss = market_value - invested
    percentage = (profit_loss / invested) * 100

    portfolio.append({
        "Ticker": ticker,
        "Buy Price": buy_price,
        "Current Price": current_price,
        "Quantity": quantity,
        "Invested Amount": invested,
        "Market Value": market_value,
        "Profit/Loss": profit_loss,
        "Gain/Loss (%)": percentage
    })

    print(f"\nStock: {ticker}")
    print(f"Total Investment: Rs. {invested:.2f}")
    print(f"Current Market Value: Rs. {market_value:.2f}")
    print(f"Profit/Loss: Rs. {profit_loss:.2f}")
    print(f"Gain/Loss: {percentage:.2f}%")

    choice = input("\nAdd another stock? (yes/no): ").strip().lower()
    if choice != "yes":
        break

if portfolio:
    total_invested = sum(item["Invested Amount"] for item in portfolio)
    total_value = sum(item["Market Value"] for item in portfolio)
    total_profit_loss = total_value - total_invested
    total_percentage = (total_profit_loss / total_invested) * 100

    print("\n" + "=" * 45)
    print("           PORTFOLIO SUMMARY")
    print("=" * 45)
    print(f"Total Investment: Rs. {total_invested:.2f}")
    print(f"Current Value: Rs. {total_value:.2f}")
    print(f"Total Profit/Loss: Rs. {total_profit_loss:.2f}")
    print(f"Overall Return: {total_percentage:.2f}%")

    filename = "portfolio_summary.csv"

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=portfolio[0].keys())
        writer.writeheader()
        writer.writerows(portfolio)

    print(f"\nPortfolio saved successfully to {filename}")
else:
    print("No stocks were added.")