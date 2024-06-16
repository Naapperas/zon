import zon

validator = zon.string().min(2).max(5).length(3)

for i in range(7):
    print(f"Checking for length={i}")

    try:
        validator.validate('a' * i)
    except zon.error.ZonError as e:
        print(f"Failed: {e}")