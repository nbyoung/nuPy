import tmp

def main():
    with tmp.Path('hello.txt') as path:
        with open(path, 'w') as file:
            file.write('Hello, world!')
        with open(path) as file:
            message = file.read()
    print(path, message)
    
main()
