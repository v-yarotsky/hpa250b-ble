default:
  @just --list

alias t := test

# run tests
test:
  poetry run pytest -vv --cov=hpa250_ble

# run test app
run:
  poetry run python ./hpa250_ble

deadcode:
  poetry run vulture \
    --min-confidence 100 \
    --ignore-names cls \
    ./hpa250_ble
