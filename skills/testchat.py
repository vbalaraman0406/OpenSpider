import sys

def main():
    print('Welcome to the Testing Chat Interface!')
    while True:
        user_input = input('> ')
        if user_input.lower() == 'exit':
            break
        else:
            print(f'You said: {user_input}')

if __name__ == '__main__':
    main()