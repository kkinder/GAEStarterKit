"""
Provides generic object listing functionality.
"""

from google.appengine.ext import ndb
import flask

from GenericViews.GenericBase import GenericBase
from util.request_util import request_wants_json


class GenericList(GenericBase):
    template = 'generic-list.html'
    table_content_template = 'component-table-content.html'

    # TODO: Add sort by
    # TODO: Add search
    # TODO: Add grouping


    def get_query(self):
        return self.model.query()

    def get(self):
        cursor = flask.request.args.get('cursor', None)

        if cursor:
            try:
                cursor = ndb.Cursor.from_websafe_string(cursor)
            except (ValueError, TypeError):
                return self.show_404()
        else:
            cursor = None

        query = self.model.query()
        rows, next_cursor, more = query.fetch_page(page_size=self.page_size, start_cursor=cursor)

        for row in rows:
            row = self.add_extra_fields(row)

        if next_cursor and more:
            next_cursor = next_cursor.to_websafe_string()
        else:
            next_cursor = None

        context = {
            self.variable_rows: rows,
            self.variable_next_cursor: next_cursor,
        }

        if request_wants_json():
            if next_cursor:
                next_url = flask.url_for(self.list_view, cursor=next_cursor)
            else:
                next_url = False
            return flask.jsonify({
                'next_cursor': next_cursor,
                'next_cursor_url': next_url,
                'content': flask.render_template(self.table_content_template, **context)
            })
        else:
            return self.render(**context)
