default:
  @just --list

alias t := test

# run tests
test:
  poetry run pytest -vv

# run test app
run:
  PYTHONPATH=$PYTHONPATH:$PWD python ./hpa250_ble
