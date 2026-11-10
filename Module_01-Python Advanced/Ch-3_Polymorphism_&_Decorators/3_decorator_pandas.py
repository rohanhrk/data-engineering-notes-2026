import pandas as pd
def pandas_decorator(fx):
    def wrapper(*args):
        response = fx(*args)

        # Do some pandas specific processing here
        response.to_parquet("Ch-3_Polymorphism_&_Decorators\\orders.parquet")
        return response
    return wrapper

@pandas_decorator
def csv_to_parquet(file_path:str):
    df = pd.read_csv(file_path)
    return df

response = csv_to_parquet("Ch-3_Polymorphism_&_Decorators\\orders.csv")
print(response.head())