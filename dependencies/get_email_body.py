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


def format_differences(old, new, link):

    # ------------------------ FORMAT THE DIFFERENCEs -------------------- #
    xslt = u'''<?xml version="1.0"?>

    <xsl:stylesheet version="1.0"
        xmlns:diff="http://namespaces.shoobx.com/diff"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

        <xsl:template name="mark-diff-insert">
            <ins class="diff-insert">
                <xsl:apply-templates/>
            </ins>
        </xsl:template>

        <xsl:template name="mark-diff-delete">
            <del class="diff-del">
                <xsl:apply-templates/>
            </del>
        </xsl:template>

        <xsl:template name="mark-diff-insert-formatting">
            <span class="diff-insert-formatting">
                <xsl:apply-templates/>
            </span>
        </xsl:template>

        <xsl:template name="mark-diff-delete-formatting">
            <span class="diff-delete-formatting">
                <xsl:apply-templates/>
            </span>
        </xsl:template>

        <!-- `diff:insert` and `diff:delete` elements are only placed around
            text. -->
        <xsl:template match="diff:insert">
            <span style="background-color:#82F67C;">
                <xsl:apply-templates/>
            </span>
        </xsl:template>

        <xsl:template match="diff:delete">
            <span style="background-color:#FF4A4A;">
                <xsl:apply-templates/>
            </span>
        </xsl:template>

        <!-- If any major paragraph element is inside a diff tag, put the markup
            around the entire paragraph. -->
        <xsl:template match="p|h1|h2|h3|h4|h5|h6">
            <xsl:choose>
                <xsl:when test="ancestor-or-self::*[@diff:insert]">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-insert" />
                    </xsl:copy>
                </xsl:when>
                <xsl:when test="ancestor-or-self::*[@diff:delete]">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-delete" />
                    </xsl:copy>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:template>

        <!-- Put diff markup in marked paragraph formatting tags. -->
        <xsl:template match="span|b|i|u|sub|sup">
            <xsl:choose>
                <xsl:when test="@diff:insert">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-insert" />
                    </xsl:copy>
                </xsl:when>
                <xsl:when test="@diff:delete">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-delete" />
                    </xsl:copy>
                </xsl:when>
                <xsl:when test="@diff:insert-formatting">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-insert-formatting" />
                    </xsl:copy>
                </xsl:when>
                <xsl:when test="@diff:delete-formatting">
                    <xsl:copy>
                        <xsl:call-template name="mark-diff-delete-formatting" />
                    </xsl:copy>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:template>

        <!-- Put diff markup into pseudo-paragraph tags, if they act as paragraph. -->
        <xsl:template match="li|th|td">
            <xsl:variable name="localParas" select="para|h1|h2|h3|h4|h5|h6" />
            <xsl:choose>
                <xsl:when test="not($localParas) and ancestor-or-self::*[@diff:insert]">
                    <xsl:copy>
                        <para>
                            <xsl:call-template name="mark-diff-insert" />
                        </para>
                    </xsl:copy>
                </xsl:when>
                <xsl:when test="not($localParas) and ancestor-or-self::*[@diff:delete]">
                    <xsl:copy>
                        <para>
                            <xsl:call-template name="mark-diff-delete" />
                        </para>
                    </xsl:copy>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:template>


        <!-- =====[ Boilerplate ]=============================================== -->

        <!-- Remove all processing information -->
        <xsl:template match="//processing-instruction()" />

        <!-- Catch all with Identity Recursion -->
        <xsl:template match="@*|node()">
            <xsl:copy>
                <xsl:apply-templates select="@*|node()"/>
            </xsl:copy>
        </xsl:template>

        <!-- Main rule for whole document -->
        <xsl:template match="/">
            <xsl:apply-templates/>
        </xsl:template>

    </xsl:stylesheet>'''
    xslt_template = lxml.etree.fromstring(xslt)

    class HTMLFormatter(formatting.XMLFormatter):
        def render(self, result):
            transform = lxml.etree.XSLT(xslt_template)
            result = transform(result)
            return super(HTMLFormatter, self).render(result)

    formatter = HTMLFormatter(text_tags=('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'),
                              formatting_tags=('b', 'u', 'i', 'em', 'super', 'sup', 'sub', 'link', 'a', 'span'))
    result = main.diff_texts(old, new, formatter=formatter)

    # -------------------------- BUILD THE HTML EMAIL BODY ------------------------------ #
    html_code = """\
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
                    <br><br><br><br>
                    """ + result + """
                    <br><br>
                </body>
            </html>
    """
    return html_code
