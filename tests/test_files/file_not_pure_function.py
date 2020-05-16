def not_pure_function(users_qs: QuerySet) -> None:
    print(f'Current amount of users is {users_qs.count()}')