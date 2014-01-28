import os
import urllib.parse

BASE_REPORT_URL = '/report'
_cwd = os.getcwd()  # prevent cwd change when load external pyd/dll modules


class Reports(list):
    pass


class ReportLink(object):
    """
    Adjust report meta object to link.
    Requires angularjs.
    """
    def __init__(self, report, app):
        self.report = report
        self.app = app
        self.filename = ''
        self.title = ''
        self.view_type = None
        self.absolute_url = None
        dirname = os.path.join(os.path.dirname(app.__file__), 'reports')
        if isinstance(report, str) and app:
            self.title = report.split('.')[0]
            self.filename = os.path.join(dirname, report)
        elif isinstance(report, (tuple, list)):
            self.title = report[0]
            filename = report[1]
            if isinstance(filename, str):
                self.filename = os.path.join(dirname, filename)
            elif isinstance(filename, dict):
                if 'file' in filename:
                    self.filename = os.path.join(dirname, filename['file'])
                else:
                    self.filename = os.path.join(dirname, self.title)
                    self.title = self.title.split('.')[0]
                self.absolute_url = filename.get('absolute_url')
        self.relpath = os.path.relpath(self.filename, _cwd)

    def get_url(self):
        return BASE_REPORT_URL + '/showreport/?report=%s&pk={{form.item.pk}}' % urllib.parse.quote(self.relpath)

    def __str__(self):
        if self.absolute_url:
            return self.absolute_url
        else:
            return '<a ng-href="%s" target="_blank">%s</a>' % (self.get_url(), self.title)
