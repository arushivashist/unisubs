// Amara, universalsubtitles.org
//
// Copyright (C) 2013 Participatory Culture Foundation
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see
// http://www.gnu.org/licenses/agpl-3.0.html.

goog.provide('unisubs.startdialog.VideoLanguages');

/**
 * @constructor
 * @param {Object} jsonVideoLanguages from widget rpc
 */
unisubs.startdialog.VideoLanguages = function(jsonVideoLanguages) {
    var videoLanguages = goog.array.map(
        jsonVideoLanguages,
        function(vljson) {
            return new unisubs.startdialog.VideoLanguage(vljson);
        });
    /**
     * @type {Array.<unisubs.startdialog.VideoLanguage>}
     */
    this.videoLanguages_ = goog.array.filter(
        videoLanguages,
        function(l) {
            return !!unisubs.languageNameForCode(l.LANGUAGE) ||
                l.SUBTITLE_COUNT > 0;
        });
    goog.array.forEach(
        this.videoLanguages_,
        function(vl) { vl.setAll(this.videoLanguages_); },
        this);
    this.languageMap_ = null;
    this.pkMap_ = null;
};

unisubs.startdialog.VideoLanguages.prototype.forEach = function(f, opt_obj) {
    goog.array.forEach(this.videoLanguages_, f, opt_obj);
};

/**
 * @param {string} language Language code
 * @returns {Array.<unisubs.startdialog.VideoLanguage>} List of video langauges for language.
 */
unisubs.startdialog.VideoLanguages.prototype.findForLanguage = function(language) {
    if (!this.languageMap_) {
        this.languageMap_ = {};
        var vl;
        for (var i = 0; i < this.videoLanguages_.length; i++) {
            vl = this.videoLanguages_[i];
            if (!this.languageMap_[vl.LANGUAGE])
                this.languageMap_[vl.LANGUAGE] = [vl];
            else
                this.languageMap_[vl.LANGUAGE].push(vl);
        }
    }
    return this.languageMap_[language] ? this.languageMap_[language] : [];
};

/**
 * @param {string} to The "to" language code
 * @param {string} from The "from" language code
 * @returns {?unisubs.startdialog.VideoLanguage} Only not null if it finds one.
 */
unisubs.startdialog.VideoLanguages.prototype.findForLanguagePair = function(to, from) {
    var langs = this.findForLanguage(to);
    return goog.array.find(
        langs,
        function(lang) {
            return lang.DEPENDENT &&
                lang.getStandardLang().LANGUAGE == from;
        });
};

unisubs.startdialog.VideoLanguages.prototype.findForPK = function(pk) {
    if (!this.pkMap_) {
        this.pkMap_ = {};
        goog.array.forEach(
            this.videoLanguages_,
            function(vl) { this.pkMap_[vl.PK] = vl; },
            this);
    }
    return this.pkMap_[pk];
};
