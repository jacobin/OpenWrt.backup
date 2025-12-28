
def divide(x, y):
    result = x / y
    return result

def process_data(a, b):
    return divide(a, b)

def main():
    num1 = 10
    num2 = 0
    result = process_data(num1, num2)
    print("Result:", result)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        #print("An error occurred:", e)
        #print("Traceback:")
        #traceback.print_exc()