import lxml
from xmldiff import main, formatting


def simple_body(link):
    email_body = """\
                                <html>
                                    <head>
                                        <meta http-equiv="Content-Type"
                                              content="text/html; charset=utf-8" />
                                        <style type="text/css">
                                            .diff-insert{background-color:#82F67C}
                                            .diff-del{background-color:#FF6666}
                                            .diff-insert-formatting{background-color:#82F67C}
                                            .diff-delete-formatting{background-color:#FF6666}
                                        </style>
                                    </head>
                                    <body>
                                        <a href='""" + link + """'>Visit web page</a>
                                    </body>
                                </html>
                        """
    return email_body
