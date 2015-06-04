window.env = window.location.search.slice(window.location.search.indexOf('mode=') + 5, -1);
console.log(window.env);
function scriptTag(cloudpath, text) {
    if (window.env == 'offline') {
        root = '/static/vendor/';
    } else {
        root = '//cdnjs.cloudflare.com/ajax/libs/' + cloudpath;
    }
    return root + text;
}
function scriptNode(src) {
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = src;
    script.async = false;
    return script;
}

var cloudflarepath = ['jquery/1.9.1/', 
                      'twitter-bootstrap/3.3.4/js/',
                      'typeahead.js/0.10.4/',
                      'jqueryui/1.11.2/',
                      'bootbox.js/4.3.0/'];
var requirements = ['jquery.min.js',
                    'bootstrap.min.js',
                    'typeahead.bundle.js',
                    'jquery-ui.min.js',
                    'bootbox.min.js'];

for (var i = 0; i < requirements.length; i++) {
    var script = scriptNode(scriptTag(cloudflarepath[i], requirements[i]));
    document.querySelector('body').appendChild(script);
}