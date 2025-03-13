import akshare as ak

def test_stock_basic_info():
    stock_code = "000001"
    stock_list = ak.stock_info_a_code_name()
    is_listed = stock_code in stock_list['code'].values
    print(f"股票 {stock_code} 是否在A股上市: {is_listed}")
    if is_listed:
        basic_info = ak.stock_individual_info_em(symbol=stock_code)
        print(basic_info)
    else:
        print(f"股票 {stock_code} 不在A股上市")

if __name__ == "__main__":
    test_stock_basic_info()

