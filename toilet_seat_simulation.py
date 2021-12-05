import argparse
import numpy as np
import os
import sys
import time

import animation


N_DAYS_IN_SIMULATION = 30  # long enough that edge behavior is insignificant
N_HRS_IN_SIMULATION = N_DAYS_IN_SIMULATION * 24

HRS_BETWEEN_1_MEAN = 5
HRS_BETWEEN_1_STD = 1

HRS_BETWEEN_2_MEAN = 24
HRS_BETWEEN_2_STD = 5

no_animation = False


# TODO: model being out of the house

def simulate_m_toilet_schedule(rand_samples, i):
    '''
    Simulates the toilet use of someone who stands up for #1. Assumes all agents
    have relieved themselves of #1 and #2 when the clock starts.
    '''
    times_m_needs_seat_up = []
    times_m_needs_seat_down = []
    cur_time_in_hrs = 0
    last_1_time = 0
    last_2_time = 0
    while cur_time_in_hrs < N_HRS_IN_SIMULATION:
        maybe_time_until_next_1 = max(
            rand_samples[i] * HRS_BETWEEN_1_STD + HRS_BETWEEN_1_MEAN,
            0,
        )
        maybe_next_1_time = last_1_time + maybe_time_until_next_1
        i += 1
        maybe_time_until_next_2 = max(
            rand_samples[i] * HRS_BETWEEN_2_STD + HRS_BETWEEN_2_MEAN,
            0,
        )
        maybe_next_2_time = last_2_time + maybe_time_until_next_2
        i += 1

        if maybe_next_1_time < maybe_next_2_time:
            # Next operation is #1
            cur_time_in_hrs = maybe_next_1_time
            times_m_needs_seat_up.append(cur_time_in_hrs)
            last_1_time = cur_time_in_hrs
        else:
            # Next operation is #2 -- and thus also resets the clock on #1
            cur_time_in_hrs = maybe_next_2_time
            times_m_needs_seat_down.append(cur_time_in_hrs)
            last_2_time = cur_time_in_hrs
            last_1_time = cur_time_in_hrs

    return i, times_m_needs_seat_up, times_m_needs_seat_down


def simulate_f_toilet_schedule(rand_samples, i):
    '''
    Simulates the toilet use of someone who sits down for #1. Assumes all agents
    have relieved themselves of #1 and #2 when the clock starts.
    '''
    times_f_needs_seat_down = []
    cur_time_in_hrs = 0
    last_1_time = 0
    last_2_time = 0
    while cur_time_in_hrs < N_HRS_IN_SIMULATION:
        # Calculate time until next 1 and 2 separately, and use the earlier one
        maybe_time_until_next_1 = max(
            rand_samples[i] * HRS_BETWEEN_1_STD + HRS_BETWEEN_1_MEAN,
            0,
        )
        maybe_next_1_time = last_1_time + maybe_time_until_next_1
        i += 1
        maybe_time_until_next_2 = max(
            rand_samples[i] * HRS_BETWEEN_2_STD + HRS_BETWEEN_2_MEAN,
            0,
        )
        maybe_next_2_time = last_2_time + maybe_time_until_next_2
        i += 1

        if maybe_next_1_time < maybe_next_2_time:
            # Next operation is #1
            cur_time_in_hrs = maybe_next_1_time
            times_f_needs_seat_down.append(cur_time_in_hrs)
            last_1_time = cur_time_in_hrs
        else:
            # Next operation is #2 -- also resets the clock on #1
            cur_time_in_hrs = maybe_next_2_time
            times_f_needs_seat_down.append(cur_time_in_hrs)
            last_2_time = cur_time_in_hrs
            last_1_time = cur_time_in_hrs

    return i, times_f_needs_seat_down


def get_operation_times_by_person(males, females):
    '''
    Simulates the toilet schedule of each person and returns the results.
    '''
    # Optimization: generate random samples all at once
    n_rand_samples = int(N_HRS_IN_SIMULATION / min(
        HRS_BETWEEN_1_MEAN,
        HRS_BETWEEN_2_MEAN,
    ) * (len(males) + len(females)) * 2 * 4)  # plenty of samples just in case

    rand_samples = np.random.randn(n_rand_samples)
    i = 0

    operation_times_by_person = {}
    for person in males:
        i, times_needs_seat_up, times_needs_seat_down = simulate_m_toilet_schedule(
            rand_samples, i)
        operation_times_by_person[person] = {
            'times_needs_seat_up': times_needs_seat_up,
            'times_needs_seat_down': times_needs_seat_down,
            'is_male': True,
        }

    for person in females:
        i, times_needs_seat_down = simulate_f_toilet_schedule(
            rand_samples, i)
        operation_times_by_person[person] = {
            'times_needs_seat_up': [],
            'times_needs_seat_down': times_needs_seat_down,
            'is_male': False,
        }

    return operation_times_by_person


def get_next_operation_time(operation_times_by_person, indices, up):
    '''
    Gets the time that the next person uses the toilet, as well as the person.
    '''
    next_time = float('inf')
    next_person = None
    for person, info in operation_times_by_person.items():
        times = (info['times_needs_seat_up']
                 if up
                 else info['times_needs_seat_down'])
        person_next_time = (times[indices[person]]
                            if indices[person] < len(times)
                            else float('inf'))
        if person_next_time < next_time:
            next_time = person_next_time
            next_person = person

    return next_time, next_person


def compute_moves_lazy_policy(operation_times_by_person):
    '''
    Computes the number of times each person has to move the position of the
    seat if the lazy policy is used.
    '''
    seat_currently_up = True
    n_moves = 0
    n_moves_by_person = {person: 0 for person in operation_times_by_person}
    up_indices = {person: 0 for person in operation_times_by_person}
    down_indices = {person: 0 for person in operation_times_by_person}

    while True:
        next_up_time, next_up_person = get_next_operation_time(
            operation_times_by_person, up_indices, up=True)

        next_down_time, next_down_person = get_next_operation_time(
            operation_times_by_person, down_indices, up=False)

        if next_up_time == float('inf') and next_down_time == float('inf'):
            # We've gotten through all operations
            break

        if next_up_time < next_down_time:
            # Next operation requires seat to be up
            if not seat_currently_up:
                n_moves += 1
                n_moves_by_person[next_up_person] += 1
            if not no_animation:
                animation.show_operation(
                    name=next_up_person,
                    is_male=operation_times_by_person[next_up_person]['is_male'],
                    seat_currently_up=seat_currently_up,
                    needs_seat_up=True,
                    n_moves=n_moves,
                )
            up_indices[next_up_person] += 1
            if not seat_currently_up:
                seat_currently_up = True
        else:
            # Next operation requires seat to be down
            if seat_currently_up:
                n_moves += 1
                n_moves_by_person[next_down_person] += 1
            if not no_animation:
                animation.show_operation(
                    name=next_down_person,
                    is_male=operation_times_by_person[next_down_person]['is_male'],
                    seat_currently_up=seat_currently_up,
                    needs_seat_up=False,
                    n_moves=n_moves,
                )
            down_indices[next_down_person] += 1
            if seat_currently_up:
                seat_currently_up = False

    return n_moves_by_person


def compute_moves_always_down_policy(operation_times_by_person):
    '''
    Computes the number of times each person has to move the position of the
    seat if the always-down policy is used.
    '''
    n_moves = 0
    up_indices = {person: 0 for person in operation_times_by_person}
    down_indices = {person: 0 for person in operation_times_by_person}

    while True:
        next_up_time, next_up_person = get_next_operation_time(
            operation_times_by_person, up_indices, up=True)

        next_down_time, next_down_person = get_next_operation_time(
            operation_times_by_person, down_indices, up=False)

        if next_up_time == float('inf') and next_down_time == float('inf'):
            # We've gotten through all operations
            break

        if next_up_time < next_down_time:
            up_indices[next_up_person] += 1
            n_moves += 2
            if not no_animation:
                animation.show_operation(
                    name=next_up_person,
                    is_male=operation_times_by_person[next_up_person]['is_male'],
                    seat_currently_up=False,
                    needs_seat_up=True,
                    n_moves=n_moves,
                    leaves_seat_down=True,
                )
        else:
            down_indices[next_down_person] += 1
            if not no_animation:
                animation.show_operation(
                    name=next_down_person,
                    is_male=operation_times_by_person[next_down_person]['is_male'],
                    seat_currently_up=False,
                    needs_seat_up=False,
                    n_moves=n_moves,
                    leaves_seat_down=True,
                )

    return {
        person: len(operation_times_by_person[person]['times_needs_seat_up']) * 2
        for person in operation_times_by_person
    }


def print_results(operation_times_by_person, *policies):
    '''
    Displays the results of the simulation.
    '''
    for moves, policy_name in policies:
        print(f'{policy_name} policy')
        print('=' * (len(policy_name) + 7))

        n_males = 0
        n_females = 0
        n_male_moves = 0
        n_female_moves = 0
        for person in operation_times_by_person:
            print(f'{person} moves: {moves[person]}')
            if operation_times_by_person[person]['is_male']:
                n_males += 1
                n_male_moves += moves[person]
            else:
                n_females += 1
                n_female_moves += moves[person]

        if n_males:
            print(f'Average male moves: {n_male_moves / n_males}')
        if n_females:
            print(f'Average female moves: {n_female_moves / n_females}')
        print(f'TOTAL MOVES: {n_male_moves + n_female_moves}')
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Compare the efficiency of different toilet seat policies.')
    parser.add_argument('-m', nargs='+', help='names of males sharing the toilet')
    parser.add_argument('-f', nargs='+', help='names of females sharing the toilet')
    parser.add_argument('--policy', type=str, help='which policy to evaluate/animate, leave blank for all')
    parser.add_argument('--no-animation', action='store_true')
    args = parser.parse_args()

    global no_animation
    no_animation = args.no_animation

    if not args.m and not args.f or len(args.m) + len(args.f) < 2:
        print('Error: Simulation must have at least two people')
        return
    if len(set(args.m).union(set(args.f))) < len(args.m) + len(args.f):
        print('Error: Each toilet user must be given a unique name')
        return
    if args.policy and args.policy not in ['lazy', 'down']:
        print(f'Error: Unknkown policy {args.policy}')
        return
    if not args.no_animation:
        if not args.policy:
            print('Error: Must provide a policy ("lazy" or "down") for animation')
            return

    if not no_animation:
        animation.set_up()

    try:
        print()
        print(f'Simulating toilet use of {len(args.m)} male(s) and {len(args.f)}'
              f' female(s) over {N_DAYS_IN_SIMULATION} days...')
        print()

        # Get one set of bathroom schedules first and then figure out it performs
        # with all policies
        operation_times_by_person = get_operation_times_by_person(args.m, args.f)
        results = []
        if args.policy != 'down':
            lazy_moves = compute_moves_lazy_policy(operation_times_by_person)
            results.append((lazy_moves, 'Lazy'))
        if args.policy != 'lazy':
            always_down_moves = compute_moves_always_down_policy(operation_times_by_person)
            results.append((always_down_moves, 'Always down'))

        print('Results:')
        print()
        print_results(operation_times_by_person, *results)
    except KeyboardInterrupt:
        if not no_animation:
            animation.take_down()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    finally:
        if not no_animation:
            animation.take_down()


if __name__ == '__main__':
    main()
