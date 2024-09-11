const axios= require("axios").default;


class Request {
    constructor(url) {
        this.url = url;
    }

    configure_request(method='get', params={}, headers={}) {
        this.method = method;
        this.params = params;
        this.headers = headers;
    }

    send_request() {
        axios.request(
            {
                "url": this.url,
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


const request = new Request("http://127.0.0.1:8000/products/latest");
request.configure_request(method="get");
request.send_request();
