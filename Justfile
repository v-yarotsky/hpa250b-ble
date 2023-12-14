default:
  @just --list

alias t := test

# run tests
test PATTERN="''":
  poetry run pytest -vv --cov=hpa250_ble -k {{PATTERN}}

# run test app
run ADDRESS="890A004D-331D-7C0D-B085-253BB7FBCB5B":
  poetry run python ./hpa250_ble --address {{ADDRESS}}

deadcode:
  poetry run vulture \
    --min-confidence 100 \
    --ignore-names cls \
    ./hpa250_ble
