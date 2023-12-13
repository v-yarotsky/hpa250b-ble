default:
  @just --list

alias t := test

# run tests
test PATTERN="*":
  poetry run pytest -vv --cov=hpa250_ble -k {{PATTERN}}

# run test app
run:
  poetry run python ./hpa250_ble

deadcode:
  poetry run vulture \
    --min-confidence 100 \
    --ignore-names cls \
    ./hpa250_ble
