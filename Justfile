default:
  @just --list

alias t := test

# run tests
test PATTERN="''":
  poetry run pytest -vv -o log_cli_level=DEBUG --cov=hpa250b_ble -k {{PATTERN}}

# run test app
run ADDRESS="890A004D-331D-7C0D-B085-253BB7FBCB5B":
  poetry run python ./hpa250b_ble --address {{ADDRESS}}

deadcode:
  poetry run vulture \
    --min-confidence 100 \
    --ignore-names cls \
    ./hpa250b_ble
