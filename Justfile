default:
  @just --list

alias t := test

# run tests
test:
  poetry run pytest -vv --cov=hpa250_ble

# run test app
run:
  PYTHONPATH=$PYTHONPATH:$PWD python ./hpa250_ble
