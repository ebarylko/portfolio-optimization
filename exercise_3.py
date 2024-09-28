# Copyright 2021 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import utilities
from dimod import ConstrainedQuadraticModel, Binaries, Binary
import utilities
from dwave.system.samplers import LeapHybridCQMSampler
from itertools import product
import numpy as np
from operator import neg

def define_variables(stockcodes):
    """Define the variables to be used for the CQM.
    Args:
        stockcodes (list): List of stocks under consideration

    Returns:
        stocks (list):
            List of variables named 's_{stk}' for each stock stk in stockcodes, where stk is replaced by the stock code.
    """

    return [Binary(f"s_{stock}") for stock in stockcodes]

def generate_unique_covar_matrix_entries(num_of_entries):
    def is_part_of_lower_triangular_matrix(point):
        return point[0] <= point[1]
    all_points = product(range(num_of_entries), repeat=2)
    return list(filter(is_part_of_lower_triangular_matrix, all_points))

def define_cqm(stocks, num_stocks_to_buy, price, returns, budget):
    """Define a CQM for the exercise.
    Requirements:
        Objective: Maximize returns
        Constraints:
            - Choose exactly num_stocks_to_buy stocks
            - Spend at most budget on purchase

    Args:
        stocks (list):
            List of variables named 's_{stk}' for each stock in stockcodes
        num_stocks_to_buy (int): Number of stocks to purchase
        price (list):
            List of current price for each stock in stocks
                where price[i] is the price for stocks[i]
        returns (list):
            List of average monthly returns for each stock in stocks
                where returns[i] is the average returns for stocks[i]
        budget (float):
            Budget for purchase

    Returns:
        cqm (ConstrainedQuadraticModel)
    """
    def extract_stock_names(stocks):
        def get_stock_name(stock):
            return stock.variables[0]

        return map(get_stock_name, stocks)

    cqm = ConstrainedQuadraticModel()

    to_buy = list(stocks)
    cqm.add_constraint(sum(to_buy) == num_stocks_to_buy, "choose k stocks")
    cqm.add_constraint_from_iterable(zip(extract_stock_names(to_buy), price),
                                     "<=",
                                     rhs=budget,
                                     label="budget_limitation")

    cqm.set_objective(sum(to_buy[i] * -returns[i] for i in range(len(to_buy))))


    return cqm

def sample_cqm(cqm):

    sampler = LeapHybridCQMSampler()
    sampleset = sampler.sample_cqm(cqm)
    return sampleset


if __name__ == '__main__':

    # 10 stocks used in this program
    stockcodes=["T", "SFL", "PFE", "XOM", "MO", "VZ", "IBM", "TSLA", "GILD", "GE"]

    # Compute relevant statistics like price, average returns, and covariance
    price, returns, variance = utilities.get_stock_info()

    # print(2 * np.triu(variance))
    num_stocks_to_buy = 2

    # Set the budget for the purchase
    budget = 80

    # Add binary variables for stocks
    stocks = define_variables(stockcodes)

    # Build CQM
    cqm = define_cqm(stocks, num_stocks_to_buy, price, returns, budget)

    # Run CQM on hybrid solver
    sampleset = sample_cqm(cqm)

    # Process and print solution
    print("\nPart 2 solution:\n")
    utilities.process_sampleset(sampleset, stockcodes)
