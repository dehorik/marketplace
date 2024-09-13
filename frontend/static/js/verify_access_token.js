function verify_access_token() {
    const access_token = get_access_token();

    if (check_access_token_exp(access_token)) {
        refresh();
    }
}


verify_access_token();