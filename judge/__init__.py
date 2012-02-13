# -*- coding: utf-8 -*-

import uuid
import binascii
from judge.utils import escape

class BaseDBObject(object):
    def __repr__(self):
        result = ", \n".join(["'%s': '%s'" % (attr, getattr(self, attr)) for attr in dir(self) if attr[0] != '_' and not callable(getattr(self, attr)) ])
        return "<{%s}>" % result
    def __getitem__(self, name):
        return getattr(self, name)
    def _init_row(self, row):
        if row:
            keys = row.keys()
            for key in keys:
                setattr(self, key, row[key])
    def e(self, name):
        if self[name]:
            return escape(self[name])
        return ""

class Member(BaseDBObject):
    username = ""
    username_lower = ""
    password = ""
    email = ""
    website = ""
    tagline = ""
    bio = ""
    create = None
    admin = 0
    lang = 1

class MemberDBMixin(object):
    def _new_member_by_row(self, row):
        member = Member()
        member._init_row(row)
        return member
    def select_member_by_id(self, mid):
        sql = """SELECT * FROM `member` WHERE `id` = '%d'""" % int(mid)
        result = self.db.get(sql)
        if result:
            return self._new_member_by_row(result)
        return None
    def select_member_by_username(self, username):
        sql = """SELECT * FROM `member` WHERE `username_lower` = '%s' LIMIT 1""" % (escape(username.lower()))
        result = self.db.get(sql)
        if result:
            return self._new_member_by_row(result)
        return None
    def select_member_by_usr_pwd(self, usr, pwd):
        sql = """SELECT * FROM `member` WHERE `username_lower` = '%s' AND `password` = '%s' LIMIT 1""" % (escape(usr.lower()), escape(pwd))
        result = self.db.get(sql)
        if result:
            return self._new_member_by_row(result)
        return None
    def select_member_by_email(self, email):
        sql = """SELECT * FROM `member` WHERE `email` = '%s' LIMIT 1""" % (escape(email.lower()))
        result = self.db.get(sql)
        if result:
            return self._new_member_by_row(result)
        return None
    def insert_member(self, member):
        member.username_lower = member.username.lower()
        sql = """INSERT INTO `member` (`username`, `username_lower`, `password`, `email`, \
                 `create`, `website`, `tagline`, `bio`, `admin`, `lang`) \
                VALUES ('%s', '%s', '%s', '%s', UTC_TIMESTAMP(), '%s', '%s', '%s', '%d', '%d')""" \
                % (member.e('username'), member.e('username_lower'), member.e('password'), member.e('email'), \
                   member.e('website'), member.e('tagline'), member.e('bio'), member.admin, member.lang)
        uid = self.db.execute(sql)
        member.id = uid
    def update_member(self, member):
        sql = """UPDATE `member` SET `password` = '%s', \
                                     `email` = '%s', \
                                     `website` = '%s', \
                                     `tagline` = '%s', \
                                     `bio` = '%s', \
                                     `admin` = '%d', \
                                     `lang` = '%d' \
                                 WHERE `id` = '%d'""" \
                 % (member.e('password'), member.e('email'), member.e('website'), member.e('tagline'), member.e('bio'), \
                    int(member.admin), int(member.lang), member.id)
        self.db.execute(sql)

class Auth(BaseDBObject):
    uid = 0
    secret = ""
    create = None

class AuthDBMixin(object):
    def _new_auth_by_row(self, row):
        if row:
            auth = Auth()
            auth._init_row(row)
            return [auth]
        return []
    def select_auth_by_uid(self, uid):
        sql = """SELECT * FROM `auth` WHERE `uid` = '%d'""" % int(uid)
        rows = self.db.query(sql)
        result = []
        for row in rows:
            result.extend(self._new_auth_by_row(row))
        return result
    def select_auth_by_secret(self, secret):
        sql = """SELECT * FROM `auth` WHERE `secret` = '%s' LIMIT 1""" % escape(secret)
        result = self._new_auth_by_row(self.db.get(sql))
        if result:
            return result[0]
        return None
    def create_auth(self, uid):
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        sql = """INSERT INTO `auth` (`uid`, `secret`, `create`) \
                 VALUES ('%d', '%s', UTC_TIMESTAMP())""" \
                 % (int(uid), random)
        self.db.execute(sql)
        auth = Auth()
        auth.uid = uid
        auth.secret = random
        return auth
    def delete_auth_by_uid(self, uid):
        sql = """DELETE FROM `auth` WHERE `uid` = '%d'""" % int(uid)
        self.db.execute(sql)
    def delete_auth_by_secret(self, secret):
        sql = """DELETE FROM `auth` WHERE `secret` = '%s'""" % (escape(secret))
        self.db.execute(sql)

class ResetMail(BaseDBObject):
    uid = 0
    secret = ""
    create = None

class ResetMailDBMixin(object):
    def _new_reset_mail_by_row(self, row):
        if row:
            auth = Auth()
            auth._init_row(row)
            return [auth]
        return []
    def select_reset_mail_by_uid(self, uid):
        sql = """SELECT * FROM `reset_mail` WHERE `uid` = '%d'""" % int(uid)
        result = []
        rows = self.db.query(sql)
        for row in rows:
            result.extend(self._new_reset_mail_by_row(row))
        return result
    def select_reset_mail_last_by_uid(self, uid):
        sql = """SELECT * FROM `reset_mail` WHERE `uid` = '%d' ORDER BY `create` DESC LIMIT 1""" % int(uid)
        auth = self._new_reset_mail_by_row(self.db.get(sql))
        if auth:
            return auth[0]
        return None
    def select_reset_mail_by_secret(self, secret):
        sql = """SELECT * FROM `reset_mail` WHERE `secret` = '%s' LIMIT 1""" % escape(secret)
        result = self._new_reset_mail_by_row(self.db.get(sql))
        if result:
            return result[0]
        return None
    def create_reset_mail(self, uid):
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        sql = """INSERT INTO `reset_mail` (`uid`, `secret`, `create`) \
                 VALUES ('%d', '%s', UTC_TIMESTAMP())""" \
                % (int(uid), random)
        self.db.execute(sql)
        reset_mail = ResetMail()
        reset_mail.uid = uid
        reset_mail.secret = random
        return reset_mail
    def delete_reset_mail_by_secret(self, secret):
        sql = """DELETE FROM `reset_mail` WHERE `secret` = '%s'""" % (escape(secret))
        self.db.execute(sql)

class Problem(BaseDBObject):
    id = 0
    title = ""
    shortname = ""
    content = ""
    content_html = ""
    inputfmt = ""
    outputfmt = ""
    samplein = ""
    sampleout = ""
    timelimit = 1000
    memlimit = 128
    tags = ""
    create = None

class ProblemDBMixin(object):
    def _new_problem_by_row(self, row):
        if row:
            problem = Problem()
            problem._init_row(row)
            return [problem]
        return []
    def insert_problem(self, problem):
        pid = self.db.execute("""INSERT INTO `problem` (`title`, `shortname`, `content`, `content_html`, \
                                 `inputfmt`, `outputfmt`, `samplein`, `sampleout`, `timelimit`, `memlimit`, `create`) \
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, UTC_TIMESTAMP())""" \
                              , problem.title, problem.shortname, problem.content, problem.content_html, \
                              problem.inputfmt, problem.outputfmt, problem.samplein, problem.sampleout, \
                              int(problem.timelimit), int(problem.memlimit))
        problem.id = pid
    def update_problem(self, problem):
        self.db.execute("""UPDATE `problem` SET `title` = %s, \
                                                `shortname` = %s, \
                                                `content` = %s, \
                                                `content_html` = %s, \
                                                `inputfmt` = %s, \
                                                `outputfmt` = %s, \
                                                `samplein` = %s, \
                                                `sampleout` = %s, \
                                                `timelimit` = %s, \
                                                `memlimit` = %s \
                                            WHERE `id` = %s""", \
                           problem.title, problem.shortname, problem.content, problem.content_html, \
                           problem.inputfmt, problem.outputfmt, problem.samplein, problem.sampleout, \
                           int(problem.timelimit), int(problem.memlimit), problem.id)
    def select_problem_by_id(self, pid):
        sql = """SELECT * FROM `problem` WHERE `id` = '%d' LIMIT 1""" % int(pid)
        query = self.db.get(sql)
        if query:
            problem = Problem()
            problem._init_row(query)
            return problem
        return None
    def select_problem_order_by_id(self, nums, start = 0):
        sql = """SELECT * FROM `problem` LIMIT %d, %d""" % (start, nums)
        result = []
        rows = self.db.query(sql)
        if rows:
            for row in rows:
                result.extend(self._new_problem_by_row(row))
        return result
    def select_problem_by_create(self, nums):
        sql = """SELECT * FROM `problem` ORDER BY `id` DESC LIMIT %d""" % nums
        result = []
        rows = self.db.query(sql)
        if rows:
            for row in rows:
                result.extend(self._new_problem_by_row(row))
        return result

class Note(BaseDBObject):
    id = 0
    title = ""
    content = ""
    member_id = 0
    create = ""
    link_problem = ""

class NoteDBMixin(object):
    def _new_problem_by_row(self, row):
        if row:
            note = Note()
            note._init_row(row)
            note.link_problem = note.link_problem.split(", ") if note.link_problem else None
            return [note]
        return []
    def select_note_by_id(self, nid):
        sql = """SELECT * FROM `note` WHERE `id` = '%d' LIMIT 1""" % int(nid)
        query = self.db.get(sql)
        if query:
            note = Note()
            note._init_row(query)
            note.link_problem = note.link_problem.split(", ") if note.link_problem else None
            return note
        return None
    def select_note_by_mid(self, mid, start = 0):
        sql = """SELECT * FROM `note` WHERE `member_id` = '%d' ORDER BY `id` DESC LIMIT %d, 10""" \
                 % (int(mid), int(start))
        query = self.db.query(sql)
        result = []
        if query:
            for row in query:
                result.extend(self._new_problem_by_row(row))
        return result
    def insert_note(self, note):
        nid = self.db.execute("""INSERT INTO `note` (`title`, `content`, `member_id`, `create`, `link_problem`) \
                                 VALUES (%s, %s, %s, UTC_TIMESTAMP(), %s)""" \
                                 , note.title, note.content, int(note.member_id), ", ".join(note.link_problem))
        note.id = nid
    def update_note(self, note):
        sql = """UPDATE `note` SET `title` = '%s', \
                                   `content` = '%s' \
                               WHERE `id` = '%d'""" \
                 % (note.title, note.content, note.id)
        self.db.execute(sql)
    def delete_note_by_nid(self, nid):
        sql = """DELETE FROM `note` WHERE `id` = '%d'""" % int(nid)
        self.db.execute(sql)
