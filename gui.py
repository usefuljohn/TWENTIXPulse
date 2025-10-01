import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pool_data_handler
from decimal import Decimal
import numpy as np
import json
import threading

class PoolPulseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PoolPulse")
        self.geometry("1024x600")

        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for labels
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)

        self.total_twentix_label = ttk.Label(top_frame, text="Total TWENTIX Amount: Fetching...", font=("Helvetica", 16))
        self.total_twentix_label.pack(side=tk.LEFT, padx=10)

        self.tvl_label = ttk.Label(top_frame, text="TVL: Fetching...", font=("Helvetica", 16))
        self.tvl_label.pack(side=tk.LEFT, padx=10)

        self.twentix_usd_price_label = ttk.Label(top_frame, text="TWENTIX/USD Price: Fetching...", font=("Helvetica", 16))
        self.twentix_usd_price_label.pack(side=tk.LEFT, padx=10)

        # Ticker frame
        ticker_frame = ttk.Frame(main_frame, height=30)
        ticker_frame.pack(fill=tk.X, pady=5)
        self.ticker_canvas = tk.Canvas(ticker_frame, bg='black', height=30)
        self.ticker_canvas.pack(fill=tk.X)
        self.ticker_text = ""
        self.ticker_x = self.winfo_width()
        self.ticker_text_id = self.ticker_canvas.create_text(self.ticker_x, 15, text=self.ticker_text, fill="white", font=("Helvetica", 12), anchor='w')
        

        # Chart frame
        chart_frame = ttk.Frame(main_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Bottom frame for button and status bar
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=5)

        self.refresh_button = ttk.Button(bottom_frame, text="Refresh", command=self.start_fetch_data_thread)
        self.refresh_button.pack(side=tk.LEFT, padx=10)

        self.status_bar = ttk.Label(bottom_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.start_fetch_data_thread()
        self.crawl_ticker()

    def crawl_ticker(self):
        self.ticker_x -= 2
        self.ticker_canvas.coords(self.ticker_text_id, self.ticker_x, 15)
        
        bbox = self.ticker_canvas.bbox(self.ticker_text_id)
        if bbox and bbox[2] < 0:
            self.ticker_x = self.winfo_width()
            self.ticker_canvas.coords(self.ticker_text_id, self.ticker_x, 15)

        self.after(20, self.crawl_ticker)


    def start_fetch_data_thread(self):
        self.refresh_button.config(state=tk.DISABLED)
        self.status_bar.config(text="Fetching data...")
        threading.Thread(target=self.fetch_data_and_update_chart, daemon=True).start()

    def fetch_data_and_update_chart(self):
        try:
            with open('config.json') as f:
                config = json.load(f)
            pool_ids = config.get("pool_ids", [])
            
            pool_data = {}
            total_twentix = Decimal(0)
            twentix_usd_price = Decimal(0)
            other_prices = {}
            ratio_42 = Decimal(0)
            ratio_248 = Decimal(0)

            for pool_id in pool_ids:
                pool_info = pool_data_handler.get_pool_data(pool_id)
                if pool_info:
                    asset_a_precision, asset_b_precision = pool_data_handler.precisions[pool_id]
                    rate_a_to_b, rate_b_to_a, balance_a, balance_b = pool_data_handler.calculate_exchange_rate(
                        pool_info,
                        asset_a_precision,
                        asset_b_precision
                    )
                    
                    if pool_id == "1.19.0": # A: BTS, B: TWENTIX
                        pool_data[pool_id] = balance_b
                        total_twentix += balance_b
                        if rate_b_to_a:
                            other_prices["BTS/TWENTIX"] = rate_b_to_a
                    elif pool_id == "1.19.41": # A: BTWTY, B: TWENTIX
                        pool_data[pool_id] = balance_b
                        total_twentix += balance_b
                    elif pool_id == "1.19.42": # A: TWENTIX, B: USD
                        total_twentix += balance_a
                        if balance_a > 0:
                            ratio_42 = balance_b / balance_a
                            other_prices["TWENTIX/HONEST.USD"] = ratio_42
                    elif pool_id == "1.19.248": # A: TWENTIX, B: XBTSX.USDC
                        pool_data[pool_id] = balance_a
                        total_twentix += balance_a
                        if balance_a > 0:
                            ratio_248 = balance_b / balance_a
                            other_prices["TWENTIX/USDC"] = ratio_248
                    elif pool_id == "1.19.44": # A: TWENTIX, B: XRP
                        pool_data[pool_id] = balance_a
                        total_twentix += balance_a
                        if rate_a_to_b:
                            other_prices["XRP/TWENTIX"] = rate_a_to_b
                    elif pool_id == "1.19.273": # A: TWENTIX, B: VAULTA
                        pool_data[pool_id] = balance_a
                        total_twentix += balance_a
                        if rate_a_to_b:
                            other_prices["VAULTA/TWENTIX"] = rate_a_to_b
                    elif pool_id == "1.19.391": # A: TWENTIX, B: HONEST.MONEY
                        pool_data[pool_id] = balance_a
                        total_twentix += balance_a
                        if rate_a_to_b:
                            other_prices["HONEST.MONEY/TWENTIX"] = rate_a_to_b
                    elif pool_id == "1.19.219": # A: TWENTIX, B: GOLDBACK
                        pool_data[pool_id] = balance_a
                        total_twentix += balance_a
                        if rate_a_to_b:
                            other_prices["GOLDBACK/TWENTIX"] = rate_a_to_b
                    elif pool_id == "1.19.468": # A: RUBLE, B: TWENTIX
                        pool_data[pool_id] = balance_b
                        total_twentix += balance_b
                        if rate_b_to_a:
                            other_prices["TWENTIX/RUBLE"] = rate_b_to_a
                    else: # For other pools, assume A is TWENTIX
                        pool_data[pool_id] = balance_a
                        total_twentix += balance_a
                else:
                    self.after(0, self.update_status, f"Failed to fetch data for pool {pool_id}")


            if ratio_248 > 0:
                twentix_usd_price = (Decimal(0.5) * ratio_42) + (Decimal(0.5) * ratio_248)
            else:
                twentix_usd_price = ratio_42

            tvl = 2 * total_twentix * twentix_usd_price

            self.after(0, self.update_ui, total_twentix, twentix_usd_price, tvl, pool_data, other_prices)

        except Exception as e:
            self.after(0, self.update_status, f"Error: {e}")
        finally:
            self.after(0, self.enable_refresh_button)


    def update_ui(self, total_twentix, twentix_usd_price, tvl, pool_data, other_prices):
        self.total_twentix_label.config(text=f"Total TWENTIX Amount: {total_twentix:.4f}")
        self.tvl_label.config(text=f"TVL: ${tvl:,.2f}")
        self.twentix_usd_price_label.config(text=f"TWENTIX/USD Price: {twentix_usd_price:.4f}")

        # Update ticker text
        ticker_items = []
        for token, price in other_prices.items():
            ticker_items.append(f"{token}: {price:.8f}")
        self.ticker_text = " | ".join(ticker_items)
        self.ticker_canvas.itemconfig(self.ticker_text_id, text=self.ticker_text)


        if total_twentix > 0:
            pool_names = {
                "1.19.0": "Pool 0: BTS",
                "1.19.44": "Pool 44: XRP",
                "1.19.273": "Pool 273: VAULTA",
                "1.19.391": "Pool 391: HONEST.MONEY",
                "1.19.41": "Pool 41: BTWTY",
                "1.19.219": "Pool 219: GOLDBACK",
                "1.19.248": "Pool 248: USDC",
                "1.19.468": "Pool 468: RUBLE"
            }
            
            chart_pool_data = {k: v for k, v in pool_data.items() if k != "1.19.42"}

            # Sort pool data by percentage in descending order for the legend
            sorted_pool_items = sorted(chart_pool_data.items(), key=lambda item: item[1], reverse=True)

            labels = [pool_names.get(p[0], f"Pool {p[0].split('.')[-1]}") for p in sorted_pool_items]
            sizes = [float(p[1] / sum(chart_pool_data.values())) * 100 for p in sorted_pool_items]
            
            self.ax.clear()
            
            wedges, _ = self.ax.pie(sizes, startangle=90)

            legend_labels = [f'{l} ({s:.1f}%)' for l, s in zip(labels, sizes)]

            self.ax.legend(wedges, legend_labels,
              title="Pools",
              loc="center right",
              bbox_to_anchor=(-0.1, 0, 0.375, 0.75))

            self.ax.set_title("TWENTIX Liquidity Network Composition")
            self.canvas.draw()
        
        self.status_bar.config(text="Data updated successfully.")

    def update_status(self, message):
        self.status_bar.config(text=message)

    def enable_refresh_button(self):
        self.refresh_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    app = PoolPulseApp()
    app.mainloop()