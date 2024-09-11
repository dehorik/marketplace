const axios= require("axios").default;


class Request {
    constructor(url) {
        this.url = url;
        this.configured_axios = axios.create(
            {
                baseURL: 'http://127.0.0.1:8000/'
            }
        );
    }

    configure_request(method='get', params={}, headers={}) {
        this.method = method;
        this.params = params;
        this.headers = headers;
    }

    send_request() {
        this.configured_axios.request(
            {
                "method": this.method,
                "headers": this.headers,
                "params": this.params
            }
        )

            .then(function (response) {
                console.log(response);
            })
            .catch(function (error) {
                console.log(error);
            })
        }
}




