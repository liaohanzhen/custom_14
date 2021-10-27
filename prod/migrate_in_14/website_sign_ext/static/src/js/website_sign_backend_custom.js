odoo.define('website_sign_ext.template', function(require) {
    'use strict';
    var template = require('website_sign.template');
    var core = require('web.core');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    
    var _t = core._t;
    var website_sign_utils = require('website_sign.utils');
    
    var CreateSignatureRequestConfirmDialog = Dialog.extend({
        template: 'website_sign_ext.create_signature_request_confirm_dialog',
        init: function(parent,templateID, options) {
            options = options || {};

            options.title = options.title || _t("Confirm Signature Sequence/Stages");
            options.size = options.size || "medium";

            options.buttons = (options.buttons || []);
            this.parent = parent;
            options.buttons.push({text: _t('Send'), classes: 'btn-primary', click: function(e) {
            	this.sendDocument();
            }});
            options.buttons.push({text: _t('Cancel'), classes: 'btn-default', close: true});
            this._super(parent, options);
            
            this.templateID = templateID;
        },
        start: function() {
        	this.$subjectInput = this.parent.$('.o_sign_subject_input').first();
            this.$messageInput = this.parent.$('.o_sign_message_textarea').first();
            this.$referenceInput = this.parent.$('.o_sign_reference_input').first();
            var sequence_partners = {}
            var waitFor = [];
            self.parent.$('.o_sign_new_signer').each(function(i, el) {
                var $elem = $(el);
                
                var partner_name = $elem.find(".select2-chosen").text();
                if (partner_name.length>0){
                	var last_index = partner_name.indexOf("(");
                	if (last_index > -1){
                		partner_name = partner_name.substring(0,last_index-1)
                	}
                	var roll_id = parseInt($elem.find('label').data('role'));
                	var sequence = parseInt($elem.find('#role_id_'+roll_id).val());
                	if (sequence in sequence_partners){
                		sequence_partners[sequence].push(partner_name);
                	}else{
                		sequence_partners[sequence] = [partner_name];
                	}
                }
            });
            var sequence_vals = Object.values(sequence_partners)
            if (NaN in sequence_partners){
            	var nan_value = sequence_vals.pop()
            	sequence_vals = [nan_value].concat(sequence_vals)
            } 
            
            var $content = $(core.qweb.render("SequenceStatus.content.desktop", {
                'widget': this, 
                'sequence_partners': sequence_vals
            }));
    		this.$('.o_sign_request_signers_sequence').first().prepend($content);
    		
        	return this._super.apply(this, arguments);
        },
        
        sendDocument: function() {
            var self = this;
            
            var completedOk = true;
            self.parent.$('.o_sign_new_signer').each(function(i, el) {
                var $elem = $(el);
                var partnerIDs = $elem.find('input[type="hidden"]').val();
                if(!partnerIDs || partnerIDs.length <= 0) {
                    completedOk = false;
                    $elem.addClass('has-error');
                    $elem.one('focusin', function(e) {
                        $elem.removeClass('has-error');
                    });
                }
            });
            if(!completedOk) {
                return false;
            }

            var waitFor = [];

            var signers = [];
            self.parent.$('.o_sign_new_signer').each(function(i, el) {
                var $elem = $(el);
                var selectDef = website_sign_utils.processPartnersSelection($elem.find('input[type="hidden"]')).then(function(partners) {
                    for(var p = 0 ; p < partners.length ; p++) {
                    	//Nilesh
                    	var roll_id = parseInt($elem.find('label').data('role'));
                    	signers.push({
                            'partner_id': partners[p],
                            'role': parseInt($elem.find('label').data('role')),
                            'sequence' : parseInt($elem.find('#role_id_'+roll_id).val())
                        });
                    }
                });
                if(selectDef !== false) {
                    waitFor.push(selectDef);
                }
            });

            var followers = [];
            var followerDef = website_sign_utils.processPartnersSelection(self.parent.$('#o_sign_followers_select')).then(function(partners) {
                followers = partners;
            });
            if(followerDef !== false) {
                waitFor.push(followerDef);
            }
            var subject = self.$subjectInput.val() || self.$subjectInput.attr('placeholder');
            var reference = self.$referenceInput.val() || self.$referenceInput.attr('placeholder');
            var message = self.$messageInput.val();
            $.when.apply($, waitFor).then(function(result) {
            	self._rpc({
                    model: 'signature.request',
                    method: 'initialize_new',
                    args: [self.templateID, signers, followers, reference, subject, message],
                })
                .then(function(sr) {
                    self.do_notify(_t("Success"), _("Your signature request has been sent."));
                    self.do_action({
                        type: "ir.actions.client",
                        tag: 'website_sign.Document',
                        name: _t("New Document"),
                        context: {
                            id: sr.id,
                            token: sr.token,
                            sign_token: sr.sign_token || null,
                            create_uid: session.uid,
                            state: 'sent',
                        },
                    });
                }).always(function() {
                	self.parent.close()
                	self.close();
                });
            });
        },
    });
    template.CreateSignatureRequestDialog.include({
    	
    	init: function(parent, templateID, rolesToChoose, templateName, attachment, options) {
            options = options || {};
            
            options.buttons = (options.buttons || []);
            options.buttons.push({text: _t('Confirm'), classes: 'btn-primary', click: function(e) {
                this.openConfirmDialog();
            }});
            
            this._super(parent, templateID, rolesToChoose, templateName, attachment, options);
            
        },
        openConfirmDialog: function(){
        	var self = this;
        	var completedOk = true;
            self.$('.o_sign_new_signer').each(function(i, el) {
                var $elem = $(el);
                var partnerIDs = $elem.find('input[type="hidden"]').val();
                if(!partnerIDs || partnerIDs.length <= 0) {
                    completedOk = false;
                    $elem.addClass('has-error');
                    $elem.one('focusin', function(e) {
                        $elem.removeClass('has-error');
                    });
                }
            });
            if(!completedOk) {
                return false;
            }
        	(new CreateSignatureRequestConfirmDialog(self,self.templateID)).open();
        },
        start: function() {
        	var res = this._super.apply(this, arguments);
        	var  send_button = _t('Send');
        	this.$footer.find('.btn-primary').each(function(i, el) {
        		var $elem = $(el);
        		if ($elem.text().indexOf(send_button)>-1){
        			$elem.remove();
        		} 
        	});
        	
        	return res;
        },
    	addSigner: function(roleID, roleName, multiple) {
            var $newSigner = $('<div/>').addClass('o_sign_new_signer form-group');
            
            $newSigner.append($('<label/>').addClass('col-md-2').text(roleName).data('role', roleID));
            //Nilesh
            var $role_seq = $('<select id="role_id_'+roleID+'"/>').addClass('col-md-1');
            var roleIDs = Object.keys(this.rolesToChoose);
            $role_seq.append('<option value=""></option>');
            
            for(var i = 0 ; i < roleIDs.length ; i++) {
            	var val = i +1 ;
            	if (val===1){
            		$role_seq.append('<option selected value="'+val+'">'+val+'</option>');
            	}
            	else{
            		$role_seq.append('<option value="'+val+'">'+val+'</option>');
            	}
            		
            }
            $newSigner.append($role_seq)
            var $signerInfo = $('<input type="hidden"/>').attr('placeholder', _t("Write email or search contact..."));
            if(multiple) {
                $signerInfo.attr('multiple', 'multiple');
            }

            var $signerInfoDiv = $('<div/>').addClass('col-md-9');
            $signerInfoDiv.append($signerInfo);

            $newSigner.append($signerInfoDiv);

            website_sign_utils.setAsPartnerSelect($signerInfo);

            this.$('.o_sign_request_signers').first().prepend($newSigner);
        },

        sendDocument: function() {
            var self = this;

            var completedOk = true;
            self.$('.o_sign_new_signer').each(function(i, el) {
                var $elem = $(el);
                var partnerIDs = $elem.find('input[type="hidden"]').val();
                if(!partnerIDs || partnerIDs.length <= 0) {
                    completedOk = false;
                    $elem.addClass('has-error');
                    $elem.one('focusin', function(e) {
                        $elem.removeClass('has-error');
                    });
                }
            });
            if(!completedOk) {
                return false;
            }
            var waitFor = [];

            var signers = [];
            self.$('.o_sign_new_signer').each(function(i, el) {
                var $elem = $(el);
                var selectDef = website_sign_utils.processPartnersSelection($elem.find('input[type="hidden"]')).then(function(partners) {
                    for(var p = 0 ; p < partners.length ; p++) {
                    	//Nilesh
                    	var roll_id = parseInt($elem.find('label').data('role'));
                    	signers.push({
                            'partner_id': partners[p],
                            'role': parseInt($elem.find('label').data('role')),
                            'sequence' : parseInt($elem.find('#role_id_'+roll_id).val())
                        });
                    }
                });
                if(selectDef !== false) {
                    waitFor.push(selectDef);
                }
            });

            var followers = [];
            var followerDef = website_sign_utils.processPartnersSelection(self.$('#o_sign_followers_select')).then(function(partners) {
                followers = partners;
            });
            if(followerDef !== false) {
                waitFor.push(followerDef);
            }

            var subject = self.$subjectInput.val() || self.$subjectInput.attr('placeholder');
            var reference = self.$referenceInput.val() || self.$referenceInput.attr('placeholder');
            var message = self.$messageInput.val();
            $.when.apply($, waitFor).then(function(result) {
            	self._rpc({
                    model: 'signature.request',
                    method: 'initialize_new',
                    args: [self.templateID, signers, followers, reference, subject, message],
                })
                .then(function(sr) {
                    self.do_notify(_t("Success"), _("Your signature request has been sent."));
                    self.do_action({
                        type: "ir.actions.client",
                        tag: 'website_sign.Document',
                        name: _t("New Document"),
                        context: {
                            id: sr.id,
                            token: sr.token,
                            sign_token: sr.sign_token || null,
                            create_uid: session.uid,
                            state: 'sent',
                        },
                    });
                }).always(function() {
                    self.close();
                    self.parent.close();
                });
            });
        },
    });
});