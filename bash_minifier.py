import webapp2
import cgi
import urllib
import minifier

class MainPage(webapp2.RequestHandler):

    def get_template(self):
        template = ""
        with open("template.html", "r") as tfile:
            template = tfile.read()
        return template

    def get(self):
        url = self.request.get("url", None)
        self.response.headers["Content-Type"] = "text/html"
        if url:
          try:
            stream = urllib.urlopen(url)
            if stream.code != 200:
                raise ValueError
            user_source = stream.read()
            return self.returnMinifiedSource(user_source)
          except:
            self.response.set_status(400)
            return self.response.write("<h1>400</h1><br>Bad url")
        params = dict(user_source="", processed_source="")
        self.response.write(self.get_template() % params)

    def post(self):
        user_source = self.request.get("user_source", "")
        self.returnMinifiedSource(user_source)

    def returnMinifiedSource(self, user_source):
        processed_source = ""
        if user_source.strip():
            processed_source = minifier.minify(user_source.replace("\r",""))
        self.response.headers["Content-Type"] = "text/html"
        params = dict(user_source=cgi.escape(user_source),
                      processed_source=cgi.escape(processed_source))
        self.response.write(self.get_template() % params)



application = webapp2.WSGIApplication([
    ("/", MainPage),
])
 

