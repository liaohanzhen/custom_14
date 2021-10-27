odoo.define('sms_on_priority.chat_manager', function (require) {
"use strict";

var chat_manager = require('mail.chat_manager');
var core = require('web.core');
var time = require('web.time');
var session = require('web.session');
var ODOOBOT_ID = "ODOOBOT";
var utils = require('mail.utils');

var emoji_substitutions = {};

chat_manager.make_message = function(data){
	var msg = {
	        id: data.id,
	        author_id: data.author_id,
	        body: data.body || "",
	        date: moment(time.str_to_datetime(data.date)),
	        message_type: data.message_type,
	        subtype_description: data.subtype_description,
	        is_author: data.author_id && data.author_id[0] === session.partner_id,
	        is_note: data.is_note,
	        is_system_notification: (data.message_type === 'notification' && data.model === 'mail.channel')
	            || data.info === 'transient_message',
	        attachment_ids: data.attachment_ids || [],
	        subject: data.subject,
	        email_from: data.email_from,
	        customer_email_status: data.customer_email_status,
	        customer_email_data: data.customer_email_data,
	        record_name: data.record_name,
	        tracking_value_ids: data.tracking_value_ids,
	        channel_ids: data.channel_ids,
	        model: data.model,
	        res_id: data.res_id,
	        sms_number_id: data.sms_number_id,
	        sms_mobile_number: data.sms_mobile_number,
	        to_mobile : data.to_mobile,
	        partner_ids : data.partner_ids,
	        url: session.url("/mail/view?message_id=" + data.id),
	    };
		
	    _.each(_.keys(emoji_substitutions), function (key) {
	        var escaped_key = String(key).replace(/([.*+?=^!:${}()|[\]\/\\])/g, '\\$1');
	        var regexp = new RegExp("(?:^|\\s|<[a-z]*>)(" + escaped_key + ")(?=\\s|$|</[a-z]*>)", "g");
	        msg.body = msg.body.replace(regexp, ' <span class="o_mail_emoji">'+emoji_substitutions[key]+'</span> ');
	    });

	    function property_descr(channel) {
	        return {
	            enumerable: true,
	            get: function () {
	                return _.contains(msg.channel_ids, channel);
	            },
	            set: function (bool) {
	                if (bool) {
	                	add_channel_to_message(msg, channel);
	                } else {
	                    msg.channel_ids = _.without(msg.channel_ids, channel);
	                }
	            }
	        };
	    }

	    Object.defineProperties(msg, {
	        is_starred: property_descr("channel_starred"),
	        is_needaction: property_descr("channel_inbox"),
	    });

	    if (_.contains(data.needaction_partner_ids, session.partner_id)) {
	        msg.is_needaction = true;
	    }
	    if (_.contains(data.starred_partner_ids, session.partner_id)) {
	        msg.is_starred = true;
	    }
	    if (msg.model === 'mail.channel') {
	        var real_channels = _.without(msg.channel_ids, 'channel_inbox', 'channel_starred');
	        var origin = real_channels.length === 1 ? real_channels[0] : undefined;
	        var channel = origin && chat_manager.get_channel(origin);
	        if (channel) {
	            msg.origin_id = origin;
	            msg.origin_name = channel.name;
	        }
	    }

	    // Compute displayed author name or email
	    if ((!msg.author_id || !msg.author_id[0]) && msg.email_from) {
	        msg.mailto = msg.email_from;
	    } else {
	        msg.displayed_author = (msg.author_id === ODOOBOT_ID) && "OdooBot" ||
	                               msg.author_id && msg.author_id[1] ||
	                               msg.email_from || _t('Anonymous');
	    }

	    // Don't redirect on author clicked of self-posted or OdooBot messages
	    msg.author_redirect = !msg.is_author && msg.author_id !== ODOOBOT_ID;

	    // Compute the avatar_url
	    if (msg.author_id === ODOOBOT_ID) {
	        msg.avatar_src = "/mail/static/src/img/odoo_o.png";
	    } else if (msg.author_id && msg.author_id[0]) {
	        msg.avatar_src = "/web/image/res.partner/" + msg.author_id[0] + "/image_small";
	    } else if (msg.message_type === 'email') {
	        msg.avatar_src = "/mail/static/src/img/email_icon.png";
	    } else {
	        msg.avatar_src = "/mail/static/src/img/smiley/avatar.jpg";
	    }

	    // add anchor tags to urls
	    msg.body = utils.parse_and_transform(msg.body, utils.add_link);

	    // Compute url of attachments
	    _.each(msg.attachment_ids, function(a) {
	        a.url = '/web/content/' + a.id + '?download=true';
	    });

	    // format date to the local only once by message
	    // can not be done in preprocess, since it alter the original value
	    if (msg.tracking_value_ids && msg.tracking_value_ids.length) {
	        _.each(msg.tracking_value_ids, function(f) {
	            if (f.field_type === 'datetime') {
	                var format = 'LLL';
	                if (f.old_value) {
	                    f.old_value = moment.utc(f.old_value).local().format(format);
	                }
	                if (f.new_value) {
	                    f.new_value = moment.utc(f.new_value).local().format(format);
	                }
	            } else if (f.field_type === 'date') {
	                var format = 'LL';
	                if (f.old_value) {
	                    f.old_value = moment(f.old_value).local().format(format);
	                }
	                if (f.new_value) {
	                    f.new_value = moment(f.new_value).local().format(format);
	                }
	            }
	        });
	    }

	    return msg;
};

function add_channel_to_message (message, channel_id) {
    message.channel_ids.push(channel_id);
    message.channel_ids = _.uniq(message.channel_ids);
}
});