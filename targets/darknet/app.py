from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DARK_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1024">
<title>DarkExchange :: Underground Market :: darkexch7v2m9k.onion</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: #1b2030;
  color: #9ba8c4;
  font-family: Tahoma, Verdana, Arial, sans-serif;
  font-size: 12px;
  line-height: 1.5;
  min-width: 900px;
}

a { color: #5b8dd9; text-decoration: none; }
a:hover { color: #7aa3e8; text-decoration: underline; }

/* ─── TOP BAR ─────────────────────────────────────────────────────────── */
#topbar {
  background: #141824;
  border-bottom: 1px solid #2d3450;
  height: 32px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  gap: 0;
}

#topbar-logo {
  color: #e0e6f8;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.02em;
  margin-right: 12px;
  white-space: nowrap;
}

#topbar-logo span { color: #5b8dd9; }

#topbar-onion {
  color: #3d4a6a;
  font-size: 11px;
  margin-right: auto;
}

#topbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 11px;
  color: #3d4a6a;
}

#topbar-right .tor-ok { color: #3db87a; font-weight: bold; }
#topbar-right .sep { color: #2d3450; }
#topbar-right .user-badge {
  background: #212638;
  border: 1px solid #2d3450;
  color: #c8d0e7;
  padding: 2px 8px;
  font-size: 11px;
}

/* ─── MAIN NAV ────────────────────────────────────────────────────────── */
#mainnav {
  background: #141824;
  border-bottom: 2px solid #5b8dd9;
  display: flex;
  align-items: stretch;
  padding: 0 8px;
}

#mainnav a {
  color: #9ba8c4;
  font-size: 12px;
  font-weight: bold;
  padding: 7px 12px;
  display: block;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  white-space: nowrap;
  text-decoration: none;
}

#mainnav a:hover { color: #e0e6f8; text-decoration: none; background: #1b2030; }
#mainnav a.active { color: #e0e6f8; border-bottom-color: #d4aa3a; background: #1b2030; }

#mainnav .nav-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 4px 4px 0;
}

#nav-search {
  background: #1b2030;
  border: 1px solid #2d3450;
  color: #c8d0e7;
  font-family: Tahoma, Verdana, sans-serif;
  font-size: 11px;
  padding: 3px 8px;
  outline: none;
  width: 150px;
}

#nav-search:focus { border-color: #5b8dd9; }
#nav-search::placeholder { color: #3d4a6a; }

#nav-search-btn {
  background: #212638;
  border: 1px solid #2d3450;
  color: #9ba8c4;
  font-family: Tahoma, Verdana, sans-serif;
  font-size: 11px;
  padding: 3px 10px;
  cursor: pointer;
}

#nav-search-btn:hover { background: #252c40; color: #e0e6f8; }

/* ─── STATS BAR ───────────────────────────────────────────────────────── */
#statsbar {
  background: #212638;
  border-bottom: 1px solid #2d3450;
  padding: 4px 10px;
  font-size: 11px;
  color: #3d4a6a;
  display: flex;
  gap: 0;
  align-items: center;
}

#statsbar .s-item { padding: 0 10px; border-right: 1px solid #2d3450; }
#statsbar .s-item:first-child { padding-left: 0; }
#statsbar .s-item:last-child { border-right: none; }
#statsbar .s-val { color: #5b8dd9; font-weight: bold; }
#statsbar .s-tor { color: #3db87a; font-weight: bold; }
#statsbar .s-right { margin-left: auto; color: #3d4a6a; }

/* ─── BREADCRUMB ──────────────────────────────────────────────────────── */
#breadcrumb {
  background: #1b2030;
  border-bottom: 1px solid #2d3450;
  padding: 5px 10px;
  font-size: 11px;
  color: #3d4a6a;
}

#breadcrumb a { color: #5b8dd9; text-decoration: none; }
#breadcrumb a:hover { text-decoration: underline; }
#breadcrumb .sep { margin: 0 4px; color: #2d3450; }
#breadcrumb .cur { color: #c8d0e7; }

/* ─── PAGE LAYOUT ─────────────────────────────────────────────────────── */
#page-wrap {
  display: flex;
  align-items: flex-start;
  gap: 0;
  padding: 10px;
}

#main-col { flex: 1; min-width: 0; }

#sidebar {
  width: 210px;
  flex-shrink: 0;
  margin-left: 10px;
}

/* ─── FORUM TABLE (categories) ────────────────────────────────────────── */
.forum-block {
  border: 1px solid #2d3450;
  margin-bottom: 10px;
}

.forum-block-title {
  background: #141824;
  border-bottom: 1px solid #2d3450;
  padding: 5px 8px;
  font-size: 12px;
  font-weight: bold;
  color: #c8d0e7;
  display: flex;
  align-items: center;
  gap: 6px;
}

.forum-block-title .fbt-icon { color: #5b8dd9; }

.cat-table {
  width: 100%;
  border-collapse: collapse;
}

.cat-table thead tr {
  background: #212638;
  border-bottom: 1px solid #2d3450;
}

.cat-table thead th {
  padding: 4px 8px;
  font-size: 10px;
  font-weight: bold;
  color: #3d4a6a;
  text-align: left;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.cat-table thead th.th-center { text-align: center; }

.cat-table tbody tr {
  border-bottom: 1px solid #2d3450;
  background: #1b2030;
}

.cat-table tbody tr:hover { background: #252c40; }
.cat-table tbody tr:last-child { border-bottom: none; }

.cat-table td { padding: 6px 8px; vertical-align: top; }
.cat-table td.td-icon { width: 32px; text-align: center; font-size: 16px; padding-top: 8px; }
.cat-table td.td-info { }
.cat-table td.td-count { width: 60px; text-align: center; color: #5b8dd9; font-weight: bold; font-size: 12px; vertical-align: middle; }
.cat-table td.td-last { width: 160px; font-size: 10px; color: #3d4a6a; vertical-align: middle; }

.cat-name { font-weight: bold; font-size: 12px; }
.cat-name a { color: #c8d0e7; text-decoration: none; }
.cat-name a:hover { color: #e0e6f8; text-decoration: underline; }
.cat-desc { font-size: 11px; color: #3d4a6a; margin-top: 1px; }

/* ─── THREAD HEADER ───────────────────────────────────────────────────── */
.thread-title-box {
  background: #212638;
  border: 1px solid #2d3450;
  border-bottom: none;
  padding: 7px 10px;
}

.thread-title-line {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-bottom: 4px;
}

.thread-sticky-badge {
  background: #e07a30;
  color: #fff;
  font-size: 10px;
  font-weight: bold;
  padding: 1px 5px;
  flex-shrink: 0;
  margin-top: 1px;
}

.thread-title-text {
  font-size: 13px;
  font-weight: bold;
  color: #e0e6f8;
  line-height: 1.3;
}

.thread-tags { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 4px; }

.ttag {
  font-size: 10px;
  font-weight: bold;
  padding: 1px 5px;
  border: 1px solid #2d3450;
  color: #3d4a6a;
}

.ttag-sale   { border-color: #c44; color: #c44; }
.ttag-hot    { border-color: #e07a30; color: #e07a30; }
.ttag-corp   { border-color: #5b8dd9; color: #5b8dd9; }
.ttag-ver    { border-color: #3db87a; color: #3db87a; }
.ttag-esc    { border-color: #d4aa3a; color: #d4aa3a; }
.ttag-new    { border-color: #3db87a; color: #3db87a; background: rgba(61,184,122,0.08); }

.thread-meta-row {
  font-size: 10px;
  color: #3d4a6a;
  display: flex;
  gap: 14px;
  margin-top: 5px;
}

.thread-meta-row .mv { color: #9ba8c4; }

/* ─── PAGINATION ──────────────────────────────────────────────────────── */
.pagination {
  background: #212638;
  border: 1px solid #2d3450;
  border-top: none;
  padding: 4px 8px;
  font-size: 11px;
  color: #3d4a6a;
  display: flex;
  align-items: center;
  gap: 0;
}

.pagination a, .pagination span {
  display: inline-block;
  padding: 1px 6px;
  border: 1px solid transparent;
  color: #5b8dd9;
  text-decoration: none;
  margin: 0 1px;
}

.pagination span.pg-cur {
  border-color: #2d3450;
  background: #1b2030;
  color: #e0e6f8;
  font-weight: bold;
}

.pagination a:hover { border-color: #3d4a6a; text-decoration: none; }
.pagination .pg-arrow { color: #9ba8c4; }

/* ─── POSTS TABLE ─────────────────────────────────────────────────────── */
.posts-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #2d3450;
}

.posts-table .pt-head {
  background: #141824;
  border-bottom: 1px solid #2d3450;
}

.posts-table .pt-head td {
  padding: 4px 8px;
  font-size: 10px;
  font-weight: bold;
  color: #3d4a6a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.posts-table .pt-row {
  border-bottom: 1px solid #2d3450;
}

.posts-table .pt-row:last-child { border-bottom: none; }
.posts-table .pt-row:nth-child(even) > td { background: #212638; }
.posts-table .pt-row:nth-child(odd) > td { background: #1b2030; }

.pt-user {
  width: 140px;
  vertical-align: top;
  padding: 10px 8px;
  border-right: 1px solid #2d3450;
  text-align: center;
}

.pt-content { vertical-align: top; padding: 0; }

/* ─── USER CARD ───────────────────────────────────────────────────────── */
.u-ava {
  width: 48px;
  height: 48px;
  background: #141824;
  border: 1px solid #2d3450;
  margin: 0 auto 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #3d4a6a;
}

.u-nick { font-size: 12px; font-weight: bold; color: #c8d0e7; margin-bottom: 3px; word-break: break-all; }

.u-rank {
  display: inline-block;
  font-size: 10px;
  font-weight: bold;
  padding: 1px 5px;
  border: 1px solid #2d3450;
  color: #3d4a6a;
  margin-bottom: 5px;
}

.u-rank-elite  { border-color: #a07a10; color: #d4aa3a; }
.u-rank-seller { border-color: #3a5a90; color: #5b8dd9; }
.u-rank-member { border-color: #2d3450; color: #9ba8c4; }
.u-rank-banned { border-color: #992200; color: #c44; background: rgba(204,68,68,0.08); }

.u-info { font-size: 10px; color: #3d4a6a; line-height: 1.9; }
.u-info .ui-v  { color: #9ba8c4; }
.u-info .ui-pos { color: #3db87a; font-weight: bold; }
.u-info .ui-neg { color: #c44; font-weight: bold; }

.u-pgp {
  margin-top: 5px;
  font-size: 9px;
  color: #2d3450;
  word-break: break-all;
  text-align: left;
  padding: 3px 4px;
  background: #141824;
  border: 1px solid #2d3450;
  line-height: 1.6;
}

/* ─── POST CONTENT ────────────────────────────────────────────────────── */
.post-header {
  background: #141824;
  border-bottom: 1px solid #2d3450;
  padding: 3px 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 10px;
  color: #3d4a6a;
}

.post-num { color: #5b8dd9; font-weight: bold; }
.post-date { }
.post-permalink { margin-left: auto; color: #3d4a6a; text-decoration: none; }
.post-permalink:hover { color: #5b8dd9; text-decoration: underline; }

.post-body-inner {
  padding: 8px 10px;
  font-size: 12px;
  color: #9ba8c4;
  line-height: 1.6;
}

.post-body-inner p { margin-bottom: 7px; }
.post-body-inner p:last-child { margin-bottom: 0; }

.post-body-inner .hl { color: #c8d0e7; font-weight: bold; }
.post-body-inner .ci {
  font-family: "Courier New", monospace;
  font-size: 11px;
  background: #141824;
  border: 1px solid #2d3450;
  padding: 0 4px;
  color: #d4aa3a;
}

.post-body-inner blockquote {
  border-left: 2px solid #3d4a6a;
  padding: 4px 10px;
  color: #3d4a6a;
  margin: 6px 0;
  font-size: 11px;
  background: #141824;
}

.post-sig {
  border-top: 1px solid #2d3450;
  margin: 8px 10px 0;
  padding: 5px 0 6px;
  font-size: 10px;
  color: #3d4a6a;
}

.post-sig .sig-pgp { color: #2d3450; word-break: break-all; }

.post-actions-row {
  border-top: 1px solid #2d3450;
  padding: 4px 8px;
  display: flex;
  gap: 0;
  align-items: center;
  background: #141824;
}

.pa-btn {
  background: none;
  border: none;
  border-right: 1px solid #2d3450;
  color: #3d4a6a;
  font-family: Tahoma, Verdana, sans-serif;
  font-size: 11px;
  padding: 2px 10px;
  cursor: pointer;
}

.pa-btn:last-child { border-right: none; }
.pa-btn:hover { color: #c8d0e7; background: #252c40; }
.pa-btn:disabled { cursor: default; opacity: 0.4; }

/* ─── BANNED OVERLAY ──────────────────────────────────────────────────── */
.banned-box {
  background: rgba(204,68,68,0.06);
  border: 1px solid #662222;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 4px 0;
}

.banned-box .bb-icon { font-size: 18px; color: #c44; flex-shrink: 0; }
.banned-title { font-size: 11px; font-weight: bold; color: #c44; }
.banned-sub { font-size: 10px; color: #992222; margin-top: 2px; }

/* ─── SUBMIT LISTING FORM ─────────────────────────────────────────────── */
.quickreply-box {
  background: #1b2030;
  border: 1px solid #2d3450;
  border-left: 3px solid #3d4a6a;
  margin: 8px 0 4px;
}

.qr-title {
  background: #141824;
  border-bottom: 1px solid #2d3450;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: bold;
  color: #9ba8c4;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.qr-body { padding: 8px; }

#paste-dump {
  width: 100%;
  min-height: 90px;
  background: #141824;
  border: 1px solid #2d3450;
  color: #c8d0e7;
  font-family: "Courier New", Courier, monospace;
  font-size: 11px;
  padding: 6px 8px;
  resize: vertical;
  outline: none;
  line-height: 1.5;
}

#paste-dump:focus { border-color: #5b8dd9; }
#paste-dump::placeholder { color: #3d4a6a; }

.qr-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 6px;
  flex-wrap: wrap;
  border-top: 1px solid #2d3450;
  padding-top: 6px;
}

.qr-req {
  font-size: 10px;
  color: #3d4a6a;
  display: flex;
  align-items: center;
  gap: 4px;
}

.chk-pass { color: #3db87a; font-weight: bold; }
.chk-fail { color: #c44; font-weight: bold; }
.chk-warn { color: #d4aa3a; }

#cred-count-badge {
  font-size: 10px;
  background: #141824;
  border: 1px solid #2d3450;
  color: #3d4a6a;
  padding: 1px 6px;
}

.val-block { margin-left: auto; text-align: right; }
.val-usd { color: #d4aa3a; font-size: 14px; font-weight: bold; }
.val-xmr { color: #a07a10; font-size: 10px; }

#btn-submit {
  width: 100%;
  margin-top: 7px;
  padding: 7px;
  background: #141824;
  border: 1px solid #2d3450;
  color: #3d4a6a;
  font-family: Tahoma, Verdana, sans-serif;
  font-size: 11px;
  font-weight: bold;
  cursor: not-allowed;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

#btn-submit.enabled {
  border-color: #5b8dd9;
  color: #e0e6f8;
  background: #212638;
  cursor: pointer;
}

#btn-submit.enabled:hover { background: #252c40; }
#btn-submit.enabled:active { background: #2a3250; }

/* ─── CRED TABLE ──────────────────────────────────────────────────────── */
.cred-table-wrap { border: 1px solid #2d3450; overflow-x: auto; margin: 8px 0 4px; }

.cred-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.cred-table th {
  background: #141824;
  color: #3d4a6a;
  font-size: 10px;
  font-weight: bold;
  text-align: left;
  padding: 4px 8px;
  border-bottom: 1px solid #2d3450;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.cred-table td {
  padding: 4px 8px;
  border-bottom: 1px solid #2d3450;
  color: #9ba8c4;
  vertical-align: middle;
}

.cred-table tr:last-child td { border-bottom: none; }
.cred-table tr:hover td { background: #252c40; }
.cred-table td.c-idx   { color: #3d4a6a; width: 24px; font-size: 10px; }
.cred-table td.c-email { color: #c8d0e7; }
.cred-table td.c-name  { color: #9ba8c4; }
.cred-table td.c-org   { color: #d4aa3a; }
.cred-table td.c-val   { color: #d4aa3a; font-weight: bold; text-align: right; white-space: nowrap; }

.tag-corp-badge {
  font-size: 9px;
  background: rgba(91,141,217,0.12);
  border: 1px solid #3a5a90;
  color: #5b8dd9;
  padding: 0 3px;
  margin-left: 4px;
}

.tag-plus-badge {
  font-size: 9px;
  background: rgba(212,170,58,0.1);
  border: 1px solid #a07a10;
  color: #d4aa3a;
  padding: 0 3px;
  margin-left: 2px;
}

/* ─── MESSAGES ────────────────────────────────────────────────────────── */
#msg-error {
  display: none;
  background: rgba(204,68,68,0.07);
  border: 1px solid #662222;
  border-left: 2px solid #c44;
  color: #c88;
  padding: 5px 8px;
  margin-top: 6px;
  font-size: 11px;
}

#msg-error::before { content: "[ОШИБКА] "; font-weight: bold; color: #c44; }

#msg-insufficient {
  display: none;
  background: rgba(212,170,58,0.07);
  border: 1px solid #a07a10;
  border-left: 2px solid #d4aa3a;
  color: #d4aa3a;
  padding: 5px 8px;
  margin-top: 5px;
  font-size: 11px;
}

/* ─── SUCCESS BOX ─────────────────────────────────────────────────────── */
#success-box {
  display: none;
  border: 1px solid #3d5a30;
  margin-top: 8px;
  overflow: hidden;
}

#success-box .sb-top {
  background: #1a2a18;
  border-bottom: 1px solid #3d5a30;
  color: #3db87a;
  font-weight: bold;
  padding: 4px 8px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

#success-box .sb-body {
  padding: 10px 12px;
  background: #1b2030;
  color: #9ba8c4;
  line-height: 1.8;
  font-size: 11px;
}

#success-box .flag-box {
  background: #141824;
  border: 1px solid #a07a10;
  border-left: 2px solid #d4aa3a;
  display: inline-block;
  padding: 5px 12px;
  margin-top: 6px;
  font-size: 13px;
  font-weight: bold;
  color: #d4aa3a;
  font-family: "Courier New", monospace;
  word-break: break-all;
}

#success-box pre {
  color: #3d4a6a;
  font-size: 10px;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  font-family: "Courier New", monospace;
}

/* ─── EMPTY STATE ─────────────────────────────────────────────────────── */
#empty-state {
  text-align: center;
  padding: 16px;
  color: #3d4a6a;
  font-size: 11px;
  background: #141824;
  border: 1px solid #2d3450;
  margin: 6px 0 4px;
}

#empty-state .es-big { font-size: 13px; font-weight: bold; color: #2d3450; margin-bottom: 5px; }
#empty-state .es-hint { color: #3d4a6a; margin-top: 4px; font-size: 10px; }

.loading-state {
  color: #3d4a6a;
  font-size: 11px;
  padding: 12px 8px;
  background: #141824;
  border: 1px solid #2d3450;
  margin: 6px 0 4px;
}

/* ─── SIDEBAR ─────────────────────────────────────────────────────────── */
.sb-block {
  border: 1px solid #2d3450;
  margin-bottom: 8px;
  font-size: 11px;
}

.sb-block-title {
  background: #141824;
  border-bottom: 1px solid #2d3450;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: bold;
  color: #9ba8c4;
}

.sb-block-body { padding: 6px 8px; background: #1b2030; }

.sb-stat-row {
  display: flex;
  justify-content: space-between;
  padding: 2px 0;
  border-bottom: 1px dotted #2d3450;
  color: #3d4a6a;
}

.sb-stat-row:last-child { border-bottom: none; }
.sb-stat-row .ssv { color: #5b8dd9; font-weight: bold; }

.online-user {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 2px 0;
  color: #9ba8c4;
  border-bottom: 1px dotted #2d3450;
}

.online-user:last-child { border-bottom: none; }

.online-dot { width: 6px; height: 6px; border-radius: 50%; background: #3db87a; display: inline-block; flex-shrink: 0; }
.online-user .ou-rank { font-size: 10px; color: #3d4a6a; }

.adv-box {
  background: #141824;
  border: 1px solid #2d3450;
  padding: 8px;
  text-align: center;
  color: #2d3450;
  font-size: 10px;
  font-style: italic;
}

/* ─── UID ERROR OVERLAY ───────────────────────────────────────────────── */
#uid-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(10,13,22,0.97);
  z-index: 9999;
  align-items: center;
  justify-content: center;
}

#uid-overlay.show { display: flex; }

#uid-box {
  background: #1b2030;
  border: 1px solid #2d3450;
  border-top: 3px solid #c44;
  padding: 24px 32px;
  max-width: 440px;
  text-align: center;
}

#uid-box .ub-title {
  color: #c44;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

#uid-box .ub-body { color: #9ba8c4; font-size: 11px; line-height: 1.7; }
#uid-box .ub-link { color: #5b8dd9; }

#uid-box .ub-code {
  color: #3d4a6a;
  font-size: 10px;
  margin-top: 14px;
  border-top: 1px solid #2d3450;
  padding-top: 10px;
  letter-spacing: 0.04em;
  font-family: "Courier New", monospace;
}

/* hidden */
#session-bar, #listing-id, #listing-id-2, #session-hash, #nav-session-id { display: none; }

/* ─── FOOTER ──────────────────────────────────────────────────────────── */
#footer {
  background: #141824;
  border-top: 1px solid #2d3450;
  padding: 8px 10px;
  font-size: 10px;
  color: #2d3450;
  text-align: center;
  line-height: 1.9;
}

#footer a { color: #3d4a6a; text-decoration: none; }
#footer a:hover { color: #5b8dd9; }
#footer .f-sep { margin: 0 8px; }
</style>
</head>
<body>

<!-- UID ERROR OVERLAY -->
<div id="uid-overlay">
  <div id="uid-box">
    <div class="ub-title">[ ОШИБКА СЕССИИ :: ДОСТУП ЗАПРЕЩЁН ]</div>
    <div class="ub-body">
      Токен сессии не предоставлен или недействителен.<br>
      Доступ возможен только по действительной реферальной ссылке.<br><br>
      Укажите ваш токен в URL:<br>
      <span class="ub-link">darkexch7v2m9k.onion/?uid=ВАШ_ТОКЕН</span>
    </div>
    <div class="ub-code">ERROR: 0x4E4F5F55494400 &nbsp;|&nbsp; SESSION_TOKEN_MISSING</div>
  </div>
</div>

<!-- TOP BAR -->
<div id="topbar">
  <div id="topbar-logo">Dark<span>Exchange</span></div>
  <div id="topbar-onion">darkexch7v2m9k.onion &bull; Underground Forum</div>
  <div id="topbar-right">
    <span class="tor-ok">&#9679; Tor: connected</span>
    <span class="sep">|</span>
    <span>NO LOGS</span>
    <span class="sep">|</span>
    <span>PGP OK</span>
    <span class="sep">|</span>
    <span id="nav-session-id"></span>
    <span class="user-badge">&#9679; ADMIN</span>
  </div>
</div>

<!-- MAIN NAV -->
<div id="mainnav">
  <a href="#">Forum</a>
  <a href="#" class="active">Market</a>
  <a href="#">Members</a>
  <a href="#">Rules</a>
  <a href="#">FAQ</a>
  <a href="#">Escrow / Гарант</a>
  <a href="#">PGP Keys</a>
  <a href="#">My Account</a>
  <div class="nav-right">
    <input id="nav-search" type="text" placeholder="Search forum...">
    <button id="nav-search-btn">Go</button>
  </div>
</div>

<!-- STATS BAR -->
<div id="statsbar">
  <div class="s-item">Threads: <span class="s-val">4,891</span></div>
  <div class="s-item">Posts: <span class="s-val">29,034</span></div>
  <div class="s-item">Members: <span class="s-val">12,847</span></div>
  <div class="s-item">Online: <span class="s-val">203</span></div>
  <div class="s-item">Tor: <span class="s-tor">connected &#10003;</span></div>
  <div class="s-right">DarkExchange v5.2.1 &bull; Time: <span id="cur-time">--:--:-- UTC</span></div>
</div>

<!-- BREADCRUMB -->
<div id="breadcrumb">
  <a href="#">Forum</a><span class="sep">&rsaquo;</span>
  <a href="#">Underground Market</a><span class="sep">&rsaquo;</span>
  <a href="#">Credentials &amp; Access</a><span class="sep">&rsaquo;</span>
  <span class="cur">Corporate Logins — email:pass dumps</span>
</div>

<!-- PAGE WRAP -->
<div id="page-wrap">

  <!-- MAIN COLUMN -->
  <div id="main-col">

    <!-- CATEGORIES TABLE -->
    <div class="forum-block">
      <div class="forum-block-title">
        <span class="fbt-icon">&#9776;</span>
        Underground Market &mdash; Категории
      </div>
      <table class="cat-table">
        <thead>
          <tr>
            <th colspan="2">Категория</th>
            <th class="th-center">Threads</th>
            <th class="th-center">Posts</th>
            <th>Last post</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="td-icon">&#128452;</td>
            <td class="td-info">
              <div class="cat-name"><a href="#">Databases &amp; Fullz</a></div>
              <div class="cat-desc">Stolen databases, personal records, fullz packages</div>
            </td>
            <td class="td-count">847</td>
            <td class="td-count">6,210</td>
            <td class="td-last">сегодня 04:12<br><a href="#">by leakm4st3r</a></td>
          </tr>
          <tr>
            <td class="td-icon">&#128179;</td>
            <td class="td-info">
              <div class="cat-name"><a href="#">Carding &amp; Dumps</a></div>
              <div class="cat-desc">CC dumps, CVV shops, BIN lists, cashout methods</div>
            </td>
            <td class="td-count">1,203</td>
            <td class="td-count">9,847</td>
            <td class="td-last">сегодня 03:58<br><a href="#">by c4rd1ng_pro</a></td>
          </tr>
          <tr>
            <td class="td-icon">&#128273;</td>
            <td class="td-info">
              <div class="cat-name"><a href="#posts-section">Credentials &amp; Access</a> <span class="ttag ttag-hot" style="font-size:9px">HOT</span></div>
              <div class="cat-desc">Corporate logins, VPN access, RDP, email:pass dumps</div>
            </td>
            <td class="td-count">634</td>
            <td class="td-count">4,521</td>
            <td class="td-last">сегодня 03:41<br><a href="#">by 0x_phantom</a></td>
          </tr>
          <tr>
            <td class="td-icon">&#128027;</td>
            <td class="td-info">
              <div class="cat-name"><a href="#">Malware &amp; Tools</a></div>
              <div class="cat-desc">RATs, stealers, exploit kits, loaders, crypters</div>
            </td>
            <td class="td-count">512</td>
            <td class="td-count">3,890</td>
            <td class="td-last">вчера 22:10<br><a href="#">by vx_underground_</a></td>
          </tr>
          <tr>
            <td class="td-icon">&#128225;</td>
            <td class="td-info">
              <div class="cat-name"><a href="#">Initial Access</a></div>
              <div class="cat-desc">Network footholds, webshells, domain access</div>
            </td>
            <td class="td-count">289</td>
            <td class="td-count">2,104</td>
            <td class="td-last">вчера 19:33<br><a href="#">by b4ckd00r_mk</a></td>
          </tr>
          <tr>
            <td class="td-icon">&#129749;</td>
            <td class="td-info">
              <div class="cat-name"><a href="#">Services</a></div>
              <div class="cat-desc">Money mule, cryptex, drop services, mixing</div>
            </td>
            <td class="td-count">406</td>
            <td class="td-count">2,462</td>
            <td class="td-last">вчера 18:07<br><a href="#">by m0n3y_m4ke</a></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- THREAD TITLE + PAGINATION -->
    <div id="posts-section">
      <div class="thread-title-box">
        <div class="thread-title-line">
          <span class="thread-sticky-badge">STICKY</span>
          <span class="thread-title-text">[SALE] Свежий дамп :: Корпоративный доступ — email:pass формат, PGP-подпись, дедупликация</span>
        </div>
        <div class="thread-tags">
          <span class="ttag ttag-sale">SALE</span>
          <span class="ttag ttag-hot">HOT</span>
          <span class="ttag ttag-corp">CORPORATE</span>
          <span class="ttag ttag-ver">PGP VERIFIED</span>
          <span class="ttag ttag-esc">ESCROW</span>
          <span class="ttag ttag-new">NEW</span>
        </div>
        <div class="thread-meta-row">
          <span>Thread #4821</span>
          <span>|</span>
          <span>Section: <span class="mv">Credentials &amp; Access</span></span>
          <span>|</span>
          <span>Replies: <span class="mv">14</span></span>
          <span>|</span>
          <span>Views: <span class="mv">3,287</span></span>
          <span>|</span>
          <span>Last reply: <span class="mv">сегодня 03:41</span></span>
        </div>
      </div>
      <div class="pagination">
        <span class="pg-arrow">&laquo; Previous</span>
        <span class="pg-cur">1</span>
        <a href="#">2</a>
        <a href="#">3</a>
        <a href="#">...</a>
        <a href="#">47</a>
        <span class="pg-arrow">Next &raquo;</span>
      </div>
    </div>

    <!-- POSTS -->
    <table class="posts-table">
      <!-- TABLE HEAD -->
      <tr class="pt-head">
        <td colspan="2">Сообщения — Страница 1 из 47</td>
      </tr>

      <!-- POST 1: 0x_phantom (seller, upload form) -->
      <tr class="pt-row">
        <td class="pt-user">
          <div class="u-ava">0x</div>
          <div class="u-nick">0x_phantom</div>
          <div class="u-rank u-rank-elite">Elite Seller</div>
          <div class="u-info">
            <div>Рег: <span class="ui-v">2021</span></div>
            <div>Посты: <span class="ui-v">1,337</span></div>
            <div>Репут: <span class="ui-pos">+2,840</span></div>
            <div>Сделок: <span class="ui-v">482</span></div>
            <div>Отзывы: &#11088;&#11088;&#11088;&#11088;&#11088;</div>
          </div>
          <div class="u-pgp">PGP: 4E2A 9B12<br>DX4A 9F03<br>FF01 C881</div>
        </td>
        <td class="pt-content">
          <div class="post-header">
            <span class="post-num">#1</span>
            <span class="post-date">06.05.2026, 00:14</span>
            <a class="post-permalink" href="#">&para; Permalink</a>
          </div>
          <div class="post-body-inner">
            <p>Продаю свежий дамп корпоративных учётных данных. Формат <span class="ci">email:pass</span>. Материал собран за последние 2 недели, дедупликация проведена.</p>
            <p>Принимаю <span class="hl">XMR / BTC</span>. Цены договорные, при объёме от 50 строк &mdash; скидка. PGP-подпись прилагается к каждому лоту.</p>
            <p>Корпоративные домены (.gov, .edu, enterprise) идут с наценкой +50%. Эскроу через гаранта форума. Vendor bond задепонирован.</p>

            <!-- SUBMIT LISTING FORM -->
            <div class="quickreply-box">
              <div class="qr-title">== Submit Listing / Загрузить свои данные == &nbsp;[форма сдачи учётных данных]</div>
              <div class="qr-body">

                <div id="msg-error"></div>

                <!-- cred table -->
                <div id="cred-table-container">
                  <div class="loading-state">Загрузка данных из хранилища...</div>
                </div>

                <textarea id="paste-dump" placeholder="user@company.com:p4ssw0rd123&#10;admin@target.org:Summer2024!&#10;john.doe@megacorp.net:Welcome1&#10;..."></textarea>

                <div class="qr-meta">
                  <div class="qr-req">
                    <span class="chk-fail" id="req-chk-min">&#10007;</span>
                    Мин. 5 записей
                    <span id="req-count-label" style="color:#3d4a6a">(0)</span>
                  </div>
                  <div class="qr-req">
                    <span class="chk-pass">&#10003;</span>
                    Дедупликация
                  </div>
                  <div class="qr-req">
                    <span class="chk-warn" id="req-chk-corp">&#9675;</span>
                    <span id="req-corp-label">+50% наценка при совпадении</span>
                  </div>
                  <div class="qr-req">
                    <span class="chk-pass">&#10003;</span>
                    PGP: 0xDX4A9F12
                  </div>
                  <span id="cred-count-badge">0 записей</span>
                  <div class="val-block">
                    <div class="val-usd" id="val-usd">$0.00</div>
                    <div class="val-xmr" id="val-xmr">0.000000 XMR</div>
                  </div>
                </div>

                <button id="btn-submit" disabled>== Выставить на продажу / Submit Listing ==</button>

                <div id="msg-insufficient"></div>

                <div id="success-box">
                  <div class="sb-top">[ СДЕЛКА ПОДТВЕРЖДЕНА — ЛИСТИНГ АКТИВЕН ]</div>
                  <div class="sb-body">
                    <pre>
Ваш пакет выставлен на продажу. Ожидается эскроу покупателя.
Транзакция записана. Средства поступят после 2 подтверждений.

ТОКЕН ВЕРИФИКАЦИИ (сохраните):
                    </pre>
                    <div class="flag-box" id="flag-display"></div>
                    <pre style="margin-top:10px">
Листинг ID  : <span id="listing-id-2" style="color:#d4aa3a">...</span>
Объём       : <span id="listing-size">0</span> учётных данных
Оцен. выпл. : <span id="listing-payout" style="color:#d4aa3a">$0.00</span>
Статус      : ОЖИДАНИЕ ПОДТВЕРЖДЕНИЯ ЭСКРОУ
++ Уведомить покупателя? [Y/n] Y — сообщение в очереди
                    </pre>
                  </div>
                </div>

              </div><!-- /qr-body -->
            </div><!-- /quickreply-box -->
          </div>
          <div class="post-sig">
            <span class="sig-pgp">PGP: 4E2A 9B12 DX4A 9F03 FF01 C881 | XMR preferred | Vendor bond: 2.0 XMR</span>
          </div>
          <div class="post-actions-row">
            <button class="pa-btn">&#9829; Like (47)</button>
            <button class="pa-btn">&#8617; Quote</button>
            <button class="pa-btn">Reply</button>
            <button class="pa-btn">Report</button>
          </div>
        </td>
      </tr>

      <!-- POST 2: r00tkit99 -->
      <tr class="pt-row">
        <td class="pt-user">
          <div class="u-ava">r0</div>
          <div class="u-nick">r00tkit99</div>
          <div class="u-rank u-rank-seller">Seller</div>
          <div class="u-info">
            <div>Рег: <span class="ui-v">2022</span></div>
            <div>Посты: <span class="ui-v">589</span></div>
            <div>Репут: <span class="ui-pos">+1,122</span></div>
          </div>
        </td>
        <td class="pt-content">
          <div class="post-header">
            <span class="post-num">#2</span>
            <span class="post-date">06.05.2026, 00:38</span>
            <a class="post-permalink" href="#">&para; Permalink</a>
          </div>
          <div class="post-body-inner">
            <p>Брал у него в прошлом месяце 50 строк корпоративных. Из них 43 живых, процент неплохой. Рекомендую, человек не кидает.</p>
            <blockquote>PGP-подпись проверил, всё чисто. Оплата XMR прошла за 10 минут.</blockquote>
            <p>Репутацию поставил, жду следующего лота с .gov доменами.</p>
          </div>
          <div class="post-actions-row">
            <button class="pa-btn">&#9829; Like (12)</button>
            <button class="pa-btn">&#8617; Quote</button>
            <button class="pa-btn">Reply</button>
            <button class="pa-btn">Report</button>
          </div>
        </td>
      </tr>

      <!-- POST 3: null_ptr -->
      <tr class="pt-row">
        <td class="pt-user">
          <div class="u-ava">NP</div>
          <div class="u-nick">null_ptr</div>
          <div class="u-rank u-rank-member">Member</div>
          <div class="u-info">
            <div>Рег: <span class="ui-v">2023</span></div>
            <div>Посты: <span class="ui-v">214</span></div>
            <div>Репут: <span class="ui-pos">+340</span></div>
          </div>
        </td>
        <td class="pt-content">
          <div class="post-header">
            <span class="post-num">#3</span>
            <span class="post-date">06.05.2026, 01:05</span>
            <a class="post-permalink" href="#">&para; Permalink</a>
          </div>
          <div class="post-body-inner">
            <p>Есть пересечения с моим дампом от february? Хочу избежать дублей перед покупкой.</p>
            <p>Домены какие? Интересуют <span class="hl">finance, healthcare, defense</span>. Готов взять крупный объём если есть такие.</p>
          </div>
          <div class="post-actions-row">
            <button class="pa-btn">&#9829; Like (3)</button>
            <button class="pa-btn">&#8617; Quote</button>
            <button class="pa-btn">Reply</button>
            <button class="pa-btn">Report</button>
          </div>
        </td>
      </tr>

      <!-- POST 4: 0x_phantom reply -->
      <tr class="pt-row">
        <td class="pt-user">
          <div class="u-ava">0x</div>
          <div class="u-nick">0x_phantom</div>
          <div class="u-rank u-rank-elite">Elite Seller</div>
          <div class="u-info">
            <div>Рег: <span class="ui-v">2021</span></div>
            <div>Посты: <span class="ui-v">1,337</span></div>
            <div>Репут: <span class="ui-pos">+2,840</span></div>
          </div>
        </td>
        <td class="pt-content">
          <div class="post-header">
            <span class="post-num">#4</span>
            <span class="post-date">06.05.2026, 01:19</span>
            <a class="post-permalink" href="#">&para; Permalink</a>
          </div>
          <div class="post-body-inner">
            <blockquote>Есть пересечения с моим дампом от february?</blockquote>
            <p>Нет пересечений &mdash; источник другой, сбор с апреля. Finance и healthcare есть, defense &mdash; в PM, публично не светим.</p>
            <p>Пиши в личку, дам превью первых 5 строк под PGP-шифрованием для верификации качества.</p>
          </div>
          <div class="post-actions-row">
            <button class="pa-btn">&#9829; Like (8)</button>
            <button class="pa-btn">&#8617; Quote</button>
            <button class="pa-btn">Reply</button>
            <button class="pa-btn">Report</button>
          </div>
        </td>
      </tr>

      <!-- POST 5: whitegirl BANNED -->
      <tr class="pt-row">
        <td class="pt-user">
          <div class="u-ava" style="color:#992222;border-color:#662222">WG</div>
          <div class="u-nick" style="color:#3d4a6a">whitegirl</div>
          <div class="u-rank u-rank-banned">BANNED</div>
          <div class="u-info">
            <div>Рег: <span class="ui-v">2024</span></div>
            <div>Посты: <span class="ui-v">12</span></div>
            <div>Репут: <span class="ui-neg">-780</span></div>
          </div>
        </td>
        <td class="pt-content">
          <div class="post-header">
            <span class="post-num">#5</span>
            <span class="post-date">06.05.2026, 02:03</span>
            <a class="post-permalink" href="#">&para; Permalink</a>
          </div>
          <div class="post-body-inner">
            <div class="banned-box">
              <span class="bb-icon">&#9940;</span>
              <div>
                <div class="banned-title">ПОЛЬЗОВАТЕЛЬ ЗАБЛОКИРОВАН</div>
                <div class="banned-sub">Сообщение скрыто администрацией. Причина: скам, нарушение правил форума.</div>
              </div>
            </div>
          </div>
          <div class="post-actions-row">
            <button class="pa-btn" disabled>&#9829; Like</button>
            <button class="pa-btn" disabled>&#8617; Quote</button>
            <button class="pa-btn" disabled>Reply</button>
          </div>
        </td>
      </tr>

      <!-- POST 6: darktr4d3r -->
      <tr class="pt-row">
        <td class="pt-user">
          <div class="u-ava">DT</div>
          <div class="u-nick">darktr4d3r</div>
          <div class="u-rank u-rank-member">Member</div>
          <div class="u-info">
            <div>Рег: <span class="ui-v">2022</span></div>
            <div>Посты: <span class="ui-v">407</span></div>
            <div>Репут: <span class="ui-pos">+615</span></div>
          </div>
        </td>
        <td class="pt-content">
          <div class="post-header">
            <span class="post-num">#6</span>
            <span class="post-date">06.05.2026, 02:47</span>
            <a class="post-permalink" href="#">&para; Permalink</a>
          </div>
          <div class="post-body-inner">
            <p>Взял 20 строк для теста &mdash; 17 живых, 3 просроченных. Для такого объёма соотношение отличное, другие продавцы хуже дают.</p>
            <p>Оплата прошла через гаранта без вопросов. Рекомендую <span class="hl">0x_phantom</span> как надёжного поставщика.</p>
          </div>
          <div class="post-actions-row">
            <button class="pa-btn">&#9829; Like (19)</button>
            <button class="pa-btn">&#8617; Quote</button>
            <button class="pa-btn">Reply</button>
            <button class="pa-btn">Report</button>
          </div>
        </td>
      </tr>

    </table><!-- /posts-table -->

    <!-- BOTTOM PAGINATION -->
    <div class="pagination" style="border:1px solid #2d3450;border-top:none">
      <span class="pg-arrow">&laquo; Previous</span>
      <span class="pg-cur">1</span>
      <a href="#">2</a>
      <a href="#">3</a>
      <a href="#">...</a>
      <a href="#">47</a>
      <span class="pg-arrow">Next &raquo;</span>
    </div>

  </div><!-- /main-col -->

  <!-- SIDEBAR -->
  <div id="sidebar">

    <div class="sb-block">
      <div class="sb-block-title">&#9679; Online Members (203)</div>
      <div class="sb-block-body">
        <div class="online-user">
          <span class="online-dot"></span>
          <span>0x_phantom</span>
          <span class="ou-rank">[Elite]</span>
        </div>
        <div class="online-user">
          <span class="online-dot"></span>
          <span>r00tkit99</span>
          <span class="ou-rank">[Seller]</span>
        </div>
        <div class="online-user">
          <span class="online-dot"></span>
          <span>null_ptr</span>
          <span class="ou-rank">[Member]</span>
        </div>
        <div class="online-user">
          <span class="online-dot"></span>
          <span>xss_admin</span>
          <span class="ou-rank">[Admin]</span>
        </div>
        <div class="online-user">
          <span class="online-dot"></span>
          <span>darktr4d3r</span>
          <span class="ou-rank">[Member]</span>
        </div>
        <div class="online-user">
          <span class="online-dot"></span>
          <span>leakm4st3r</span>
          <span class="ou-rank">[Seller]</span>
        </div>
        <div style="color:#3d4a6a;font-size:10px;margin-top:4px;padding-top:4px;border-top:1px dotted #2d3450">
          + 197 guests / Tor users
        </div>
      </div>
    </div>

    <div class="sb-block">
      <div class="sb-block-title">Forum Statistics</div>
      <div class="sb-block-body">
        <div class="sb-stat-row"><span>Threads</span><span class="ssv">4,891</span></div>
        <div class="sb-stat-row"><span>Posts</span><span class="ssv">29,034</span></div>
        <div class="sb-stat-row"><span>Members</span><span class="ssv">12,847</span></div>
        <div class="sb-stat-row"><span>Online</span><span class="ssv">203</span></div>
        <div class="sb-stat-row"><span>Uptime</span><span style="color:#3db87a;font-weight:bold">99.7%</span></div>
      </div>
    </div>

    <div class="sb-block">
      <div class="sb-block-title">Market Rates</div>
      <div class="sb-block-body">
        <div class="sb-stat-row"><span>XMR/USD</span><span class="ssv">$172.40</span></div>
        <div class="sb-stat-row"><span>BTC/USD</span><span class="ssv">$63,240</span></div>
        <div class="sb-stat-row"><span>Base/record</span><span class="ssv">$4.25</span></div>
        <div class="sb-stat-row"><span>Corp +50%</span><span style="color:#d4aa3a;font-weight:bold">$6.38</span></div>
      </div>
    </div>

    <div class="adv-box">
      [ РЕКЛАМА ]<br>
      Размещение: adv@darkexch7v2m9k.onion
    </div>


    <div class="sb-block" id="mission-block" style="border-top:2px solid #d4aa3a">
      <div class="sb-block-title" style="color:#d4aa3a">&#9888; ACTIVE MISSION</div>
      <div class="sb-block-body" style="font-size:10px;line-height:1.8">
        <div style="color:#c8d0e7;font-weight:bold;margin-bottom:4px">Credential Harvest Operation</div>
        <div style="color:#3d4a6a;margin-bottom:6px">Obtain 5 valid corporate logins and list them for sale to receive your payment token.</div>
        <div class="sb-stat-row"><span>Required</span><span style="color:#d4aa3a;font-weight:bold">5 valid creds</span></div>
        <div class="sb-stat-row"><span>Harvested</span><span class="ssv" id="mission-harvested">0</span></div>
        <div class="sb-stat-row"><span>Status</span><span id="mission-status" style="color:#c44">PENDING</span></div>
      </div>
    </div>

  </div><!-- /sidebar -->

</div><!-- /page-wrap -->

<!-- hidden session elements -->
<span id="session-hash"></span>
<span id="listing-id"></span>
<span id="nav-session-id"></span>

<!-- FOOTER -->
<div id="footer">
  DarkExchange v5.2.1 &nbsp;|&nbsp; Powered by XenForo&trade; &nbsp;|&nbsp; Tor: darkexch7v2m9k.onion<br>
  Uptime: 99.7% &nbsp;|&nbsp; Current time: <span id="footer-time">--:-- UTC</span> &nbsp;|&nbsp; All times UTC<br>
  Support: <a href="#">support@darkexch7v2m9k.onion</a> &nbsp;|&nbsp; PGP: 4E2A 9B12 DX4A 9F03
</div>

<script>
(function () {
  'use strict';

  const $ = id => document.getElementById(id);

  function randomHex(len) {
    let h = '';
    const chars = '0123456789abcdef';
    for (let i = 0; i < len; i++) h += chars[Math.floor(Math.random() * 16)];
    return h;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  const CORP_DOMAINS = [
    'megacorp','corp','enterprise','inc','ltd','solutions',
    'tech','systems','group','global','finance','bank','gov',
    'edu','health','pharma','defense','secure'
  ];

  function isCorporate(email) {
    const domain = (email.split('@')[1] || '').toLowerCase();
    return CORP_DOMAINS.some(kw => domain.includes(kw)) || domain.endsWith('.gov') || domain.endsWith('.edu');
  }

  function calcValue(count, hasCorp) {
    const base = count * 4.25;
    const multiplier = hasCorp ? 1.5 : 1.0;
    return base * multiplier;
  }

  function updateValueDisplay(count, hasCorp) {
    const usd = calcValue(count, hasCorp);
    $('val-usd').textContent = '$' + usd.toFixed(2);
    $('val-xmr').textContent = (count * 0.000138).toFixed(6) + ' XMR';
  }

  function parseLines() {
    const raw = $('paste-dump').value.trim();
    if (!raw) return [];
    return raw.split('\\n')
      .map(l => l.trim())
      .filter(l => l.includes(':') && l.length > 4);
  }

  function updateRequirements() {
    const lines = parseLines();
    const count = lines.length;
    const hasCorp = lines.some(l => isCorporate(l.split(':')[0] || ''));

    const chkMin = $('req-chk-min');
    if (count >= 5) {
      chkMin.textContent = '✓';
      chkMin.className = 'chk-pass';
    } else {
      chkMin.textContent = '✗';
      chkMin.className = 'chk-fail';
    }
    $('req-count-label').textContent = '(' + count + ')';

    const chkCorp = $('req-chk-corp');
    if (hasCorp) {
      chkCorp.textContent = '✓';
      chkCorp.className = 'chk-pass';
      $('req-corp-label').textContent = '+50% НАЦЕНКА ПРИМЕНЕНА';
    } else {
      chkCorp.textContent = '○';
      chkCorp.className = 'chk-warn';
      $('req-corp-label').textContent = '+50% наценка при совпадении';
    }

    updateValueDisplay(count, hasCorp);
    $('cred-count-badge').textContent = count + ' записей';

    const btn = $('btn-submit');
    if (count >= 5) {
      btn.disabled = false;
      btn.classList.add('enabled');
    } else {
      btn.disabled = true;
      btn.classList.remove('enabled');
    }

    return { count, hasCorp, lines };
  }

  function renderCredTable(creds) {
    const container = $('cred-table-container');

    if (!creds || creds.length === 0) {
      container.innerHTML =
        '<div id="empty-state">' +
        '<div class="es-big">[ ХРАНИЛИЩЕ ПУСТО ]</div>' +
        'Нет учётных данных в хранилище.<br>' +
        '<span class="es-hint">Завершите фишинговую кампанию и загрузите собранные данные ниже.</span>' +
        '</div>';
      return;
    }

    let rows = '';
    creds.forEach((c, i) => {
      const email = escapeHtml(c.email || c.username || '');
      const name  = escapeHtml(c.name || c.target_name || '—');
      const org   = escapeHtml(c.organization || c.org || '—');
      const corp  = isCorporate(email);
      const val   = corp ? '$6.38' : '$4.25';
      const badge = corp
        ? '<span class="tag-corp-badge">CORP</span><span class="tag-plus-badge">+50%</span>'
        : '';
      rows +=
        '<tr>' +
        '<td class="c-idx">' + (i + 1) + '</td>' +
        '<td class="c-name">' + name + '</td>' +
        '<td class="c-email">' + email + badge + '</td>' +
        '<td class="c-org">' + org + '</td>' +
        '<td class="c-val">' + val + '</td>' +
        '</tr>';
    });

    container.innerHTML =
      '<div class="cred-table-wrap">' +
      '<table class="cred-table">' +
      '<thead><tr>' +
      '<th>#</th><th>Цель</th><th>Email / Логин</th><th>Организация</th><th>Оценка</th>' +
      '</tr></thead>' +
      '<tbody>' + rows + '</tbody>' +
      '</table></div>';
  }

  function prefillTextarea(creds) {
    if (!creds || creds.length === 0) return;
    const lines = creds.map(c => {
      const login = c.email || c.username || '';
      const pass  = c.password || c.pass || 'harvested';
      return login + ':' + pass;
    });
    $('paste-dump').value = lines.join('\\n');
    updateRequirements();
  }

  // Clock
  function updateClock() {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    const t = pad(now.getUTCHours()) + ':' + pad(now.getUTCMinutes()) + ':' + pad(now.getUTCSeconds()) + ' UTC';
    const el1 = $('cur-time');
    const el2 = $('footer-time');
    if (el1) el1.textContent = t;
    if (el2) el2.textContent = t;
  }
  updateClock();
  setInterval(updateClock, 1000);

  // Init session
  const params = new URLSearchParams(window.location.search);
  const uid = params.get('uid') || params.get('user_id');

  const sessionHash = 'anon-' + randomHex(8);
  const sh = $('session-hash');
  if (sh) sh.textContent = sessionHash;
  const nsi = $('nav-session-id');
  if (nsi) nsi.textContent = 'SESSION: ' + sessionHash.toUpperCase();
  const listingId = 'DX-' + randomHex(12).toUpperCase();
  const li = $('listing-id');
  if (li) li.textContent = listingId;
  const li2 = $('listing-id-2');
  if (li2) li2.textContent = listingId;

  $('paste-dump').addEventListener('input', updateRequirements);
  updateRequirements();

  // Fetch market data
  if (!uid) return;
  const fetchUrl = 'http://localhost:8000/api/phish/market-data?user_id=' + encodeURIComponent(uid);
  fetch(fetchUrl)
    .then(r => r.json())
    .then(data => {
      const creds = data.credentials || data.creds || [];
      renderCredTable(creds);
      prefillTextarea(creds);
      const count_val = creds ? creds.length : 0;
      const mh = document.getElementById('mission-harvested');
      const ms = document.getElementById('mission-status');
      if (mh) mh.textContent = count_val;
      if (ms) {
        if (count_val >= 5) {
          ms.textContent = 'READY TO LIST';
          ms.style.color = '#3db87a';
        } else {
          ms.textContent = count_val + '/5 — INCOMPLETE';
          ms.style.color = '#d4aa3a';
        }
      }
    })
    .catch(() => {
      $('cred-table-container').innerHTML =
        '<div id="empty-state">' +
        '<div class="es-big">[ ХРАНИЛИЩЕ ПУСТО ]</div>' +
        'Нет учётных данных в хранилище.<br>' +
        '<span class="es-hint">Завершите фишинговую кампанию и загрузите собранные данные ниже.</span>' +
        '</div>';
    });

  // Submit
  $('btn-submit').addEventListener('click', function () {
    const { count, hasCorp } = updateRequirements();

    if (count < 5) {
      const need = 5 - count;
      const insuf = $('msg-insufficient');
      insuf.style.display = 'block';
      insuf.textContent = 'НЕДОСТАТОЧНО ДАННЫХ — нужно ещё ' + need + ' записей для выставления лота.';
      return;
    }

    $('msg-insufficient').style.display = 'none';

    const btn = $('btn-submit');
    btn.textContent = '[ Отправка — шифрование данных... ]';
    btn.disabled = true;
    btn.classList.remove('enabled');

    const payload = {
      user_id: parseInt(uid, 10),
      credentials: $('paste-dump').value
    };

    fetch('http://localhost:8000/api/phish/market-submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          $('success-box').style.display = 'block';
          $('flag-display').textContent = data.flag || 'SF{m4ss_ph1sh_h4rv3st}';
          $('listing-size').textContent = count;
          $('listing-payout').textContent = '$' + calcValue(count, hasCorp).toFixed(2);
          btn.textContent = '[ Листинг подтверждён ]';
          btn.style.borderColor = '#2d3450';
          btn.style.color = '#3d4a6a';
          $('success-box').scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
          const need = data.needed || (5 - count);
          const insuf = $('msg-insufficient');
          insuf.style.display = 'block';
          insuf.textContent = data.message || ('НЕДОСТАТОЧНО ДАННЫХ — нужно ещё ' + need + ' учётных записей');
          btn.textContent = '== Выставить на продажу / Submit Listing ==';
          btn.disabled = false;
          btn.classList.add('enabled');
        }
      })
      .catch(err => {
        $('msg-error').style.display = 'block';
        $('msg-error').textContent = 'Ошибка сети: ' + (err.message || 'неизвестно');
        btn.textContent = '== Выставить на продажу / Submit Listing ==';
        btn.disabled = false;
        btn.classList.add('enabled');
      });
  });

})();
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return DARK_HTML


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9005)
