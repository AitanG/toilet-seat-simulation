import copy
import curses
import time


BLANK_FRAME = [[' ' for _ in range(100)] for _ in range(36)]  # same dims as ASCII art
SEAT_UP_ASCII = []
SEAT_HALFWAY_ASCII = []
SEAT_DOWN_ASCII = []
MALE_SIGN_ASCII = []
MALE_SIGN_ENTERING_ASCII = []
FEMALE_SIGN_ASCII = []
FEMALE_SIGN_ENTERING_ASCII = []

ASCII_CACHE = {}


def superimpose(frame1, frame2):
    '''
    Create a new frame superimposing frame2 onto frame1, with preference for
    frame2 chars.
    '''
    result = copy.deepcopy(frame1)
    for i, line in enumerate(frame2):
        for j, char in enumerate(line):
            if char != ' ':
                result[i][j] = char  
    return result


def show_frame(*args):
    '''
    Render a single frame of the simulation.
    '''
    if args not in ASCII_CACHE:
        name, is_male, person_percent, lid_percent = args
        frame = BLANK_FRAME

        # Add toilet
        if lid_percent == 0:
            frame = superimpose(frame, SEAT_DOWN_ASCII)
        elif lid_percent == 0.5:
            frame = superimpose(frame, SEAT_HALFWAY_ASCII)
        elif lid_percent == 1:
            frame = superimpose(frame, SEAT_UP_ASCII)

        # Add male/female sign
        if person_percent == 0.5:
            if is_male:
                frame = superimpose(frame, MALE_SIGN_ENTERING_ASCII)
            else:
                frame = superimpose(frame, FEMALE_SIGN_ENTERING_ASCII)
        elif person_percent == 1:
            if is_male:
                frame = superimpose(frame, MALE_SIGN_ASCII)
            else:
                frame = superimpose(frame, FEMALE_SIGN_ASCII)

        # Add name
        name_frame = copy.deepcopy(BLANK_FRAME)
        if person_percent:
            name_start_col = 69 if person_percent == 0.5 else 54
            for i, char in enumerate(name):
                name_frame[26][name_start_col + i] = '='
                name_frame[27][name_start_col + i] = char
                name_frame[28][name_start_col + i] = '='
            frame = superimpose(frame, name_frame)

        global ASCII_CACHE
        ASCII_CACHE[args] = frame

    stdscr.addstr(0, 0, ASCII_CACHE[frame])
    stdscr.refresh()


def show_operation(name, is_male, seat_currently_up, needs_seat_up, leaves_seat_down=False):
    '''
    Render a sequence of frames to simulate one operation.
    '''
    lid_percents = [0] * 3
    if seat_currently_up:
        lid_percents[0] = 1
        if needs_seat_up:
            lid_percents[1] = 1
            lid_percents[2] = 1
        else:
            lid_percents[1] = 0.5
            lid_percents[2] = 0
    else:
        lid_percents[0] = 0
        if needs_seat_up:
            lid_percents[1] = 0.5
            lid_percents[2] = 1
        else:
            lid_percents[1] = 0
            lid_percents[2] = 0

    show_frame(name, is_male, person_percent=0.5, lid_percent=lid_percents[0])
    show_frame(name, is_male, person_percent=1, lid_percent=lid_percents[0])
    show_frame(name, is_male, person_percent=1, lid_percent=lid_percents[1])
    show_frame(name, is_male, person_percent=1, lid_percent=lid_percents[2])

    if needs_seat_up and leaves_seat_down:
        show_frame(name, is_male, person_percent=1, lid_percent=0.5)
        show_frame(name, is_male, person_percent=1, lid_percent=0)
        show_frame(name, is_male, person_percent=0.5, lid_percent=0)
        show_frame(name, is_male, person_percent=0, lid_percent=0)
    else:
        show_frame(name, is_male, person_percent=0.5, lid_percent=lid_percents[2])
        show_frame(name, is_male, person_percent=0, lid_percent=lid_percents[2])


def load_file(file):
    '''
    Convert ASCII art file into a 2D array of chars.
    '''
    return [[c for c in line.strip()] for line in file.read().split('\n')]


def set_up():
    '''
    Load ASCII art and set up curses canvas.
    '''
    global SEAT_UP_ASCII, SEAT_HALFWAY_ASCII, SEAT_DOWN_ASCII, MALE_SIGN_ASCII, MALE_SIGN_ENTERING_ASCII, FEMALE_SIGN_ASCII, FEMALE_SIGN_ENTERING_ASCII

    with open('ascii-art/seat-up-ascii.txt', 'r') as f:
        SEAT_UP_ASCII = load_file(f)
    with open('ascii-art/seat-halfway-ascii.txt', 'r') as f:
        SEAT_HALFWAY_ASCII = load_file(f)
    with open('ascii-art/seat-down-ascii.txt', 'r') as f:
        SEAT_DOWN_ASCII = load_file(f)
    with open('ascii-art/male-sign-ascii.txt', 'r') as f:
        MALE_SIGN_ASCII = load_file(f)
    with open('ascii-art/male-sign-entering-ascii.txt', 'r') as f:
        MALE_SIGN_ENTERING_ASCII = load_file(f)
    with open('ascii-art/female-sign-ascii.txt', 'r') as f:
        FEMALE_SIGN_ASCII = load_file(f)
    with open('ascii-art/female-sign-entering-ascii.txt', 'r') as f:
        FEMALE_SIGN_ENTERING_ASCII = load_file(f)

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()


def take_down():
    '''
    Clear curses canvas.
    '''
    curses.echo()
    curses.nocbreak()
    curses.endwin()
