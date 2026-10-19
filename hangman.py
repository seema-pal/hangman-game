import random
words = ["python", "computer", "program", "coding", "hangman"]
# Step 4: ASCII Hangman stages
HANGMAN_PICS = [
    """
     +---+
         |
         |
         |
        ===""",
    """
     +---+
     O   |
         |
         |
        ===""",
    """
     +---+
     O   |
     |   |
         |
        ===""",
    """
     +---+
     O   |
    /|   |
         |
        ===""",
    """
     +---+
     O   |
    /|\\  |
         |
        ===""",
    """
     +---+
     O   |
    /|\\  |
    /    |
        ===""",
    """
     +---+
     O   |
    /|\\  |
    / \\  |
        ==="""
]
def play_hangman():
    secret_word = random.choice(words)
    guessed_letters = set()
    wrong_guesses = 0
    max_attempt = 6
    print("welcome to hangman!")
    print("guess the hidden word, one letter at a time. ")
    while wrong_guesses < max_attempt:
        display_word = " "
        for letter in secret_word:
            if letter in guessed_letters:
                display_word +=  " "
            else:
                display_word += "_"
        print("/nword:",  display_word)
        print("wrong guesses: ", wrong_guesses, "/", max_attempt)
        print("guessed letters: ", sorted(guessed_letters))
        print(HANGMAN_PICS[wrong_guesses])
        if all(letter in guessed_letters for letter in secret_word):
            print("congratulation! you win!")
            return
        guess = input("enter a single letter: ").strip().lower()
        if len (guess) != 1 or not guess.isalpha():
            print("please enter only one alphabet letter. ")
            continue
        #prevent duplicate guesses
        if guess in guessed_letters:
            print("you already guessed that letter!")
            continue
        guessed_letters.add(guess)
        if guess in secret_word:
            print("correct guess!")
        else:
            wrong_guesses += 1
            print("wrong guess!")
    print("game over! you lost.")
    print("The word was:", secret_word)
if __name__=="__main__":
    play_hangman()
