FROM nginx@sha256:54f2a904c251d5a34adf545a72d32515a15e08418dae0266e23be2e18c66fefa

COPY index.html dashboard.html login.html app.js site.css sw.js manifest.webmanifest icon.svg /usr/share/nginx/html/
COPY docs/ /usr/share/nginx/html/docs/

EXPOSE 80
