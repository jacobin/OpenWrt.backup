###############################################################################
# https://www.google.com/search?q=python+%E5%8F%82%E6%95%B0+*&pws=0&gl=us&gws_rd=cr

###############################################################################
print("Example 1")
def print_args(*args):
    print(type(args))  # <class 'tuple'>
    print(args)        # (1, 'hello', 3.14)

print_args(1, 'hello', 3.14)

my_list = [1, 2, 3]
def print_list_items(*items):
    for item in items:
        print(item)

print_list_items(*my_list) # 解包列表，等同于 print_list_items(1, 2, 3)

###############################################################################
print("\nExample 2")
def print_kwargs(**kwargs):
    print(type(kwargs)) # <class 'dict'>
    print(kwargs)       # {'name': 'Alice', 'age': 30}

print_kwargs(name='Alice', age=30)

my_dict = {'city': 'New York', 'country': 'USA'}
def print_dict_items(**items):
    for key, value in items.items():
        print(f"{key}: {value}")

print_dict_items(**my_dict) # 解包字典，等同于 print_dict_items(city='New York', country='USA')

###############################################################################
print("\nExample 3")
def complex_func(a, b, *args, kw_only, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"kw_only={kw_only}")
    print(f"kwargs={kwargs}")

complex_func(1, 2, 3, 4, kw_only='hello', name='Bob', age=25)
# 输出：
#     a=1, b=2
#     args=(3, 4)
#     kw_only=hello
#     kwargs={'name': 'Bob', 'age': 25}
