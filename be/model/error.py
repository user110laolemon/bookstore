error_code = {
    401: "authorization fail.",
    511: "non exist user id {}",
    512: "exist user id {}",
    513: "non exist store id {}",
    514: "exist store id {}",
    515: "non exist book id {}",
    516: "exist book id {}",
    517: "stock level low, book id {}",
    518: "invalid order id {}",
    519: "not sufficient funds, order id {}",
    520: "order status error, order id {}",  # 添加订单状态错误信息
    521: "non exist order id {}",  # 添加订单不存在错误信息
    522: "database error",  # 数据库错误
    523: "invalid parameter",  # 无效参数
    524: "purchase order failed",  # 购买订单失败
    525: "seller authorization fail",  # 卖家授权失败
    526: "buyer authorization fail",  # 买家授权失败
    527: "invalid store authorization",  # 无效的商店授权
    528: "database operation error",  # 数据库操作错误
}


def error_non_exist_user_id(user_id):
    return 511, error_code[511].format(user_id)


def error_exist_user_id(user_id):
    return 512, error_code[512].format(user_id)


def error_non_exist_store_id(store_id):
    return 513, error_code[513].format(store_id)


def error_exist_store_id(store_id):
    return 514, error_code[514].format(store_id)


def error_non_exist_book_id(book_id):
    return 515, error_code[515].format(book_id)


def error_exist_book_id(book_id):
    return 516, error_code[516].format(book_id)


def error_stock_level_low(book_id):
    return 517, error_code[517].format(book_id)


def error_invalid_order_id(order_id):
    return 518, error_code[518].format(order_id)


def error_not_sufficient_funds(order_id):
    return 519, error_code[519].format(order_id)


def error_status_fail(order_id):
    return 520, error_code[520].format(order_id)


def error_non_exist_order_id(order_id):
    return 521, error_code[521].format(order_id)


def error_database():
    return 522, error_code[522]


def error_invalid_parameter():
    return 523, error_code[523]


def error_purchase_fail():
    return 524, error_code[524]


def error_seller_auth_fail():
    return 525, error_code[525]


def error_buyer_auth_fail():
    return 526, error_code[526]


def error_store_auth_fail():
    return 527, error_code[527]


def error_database_operation():
    return 528, error_code[528]


def error_authorization_fail():
    return 401, error_code[401]


def error_and_message(code, message):
    return code, message