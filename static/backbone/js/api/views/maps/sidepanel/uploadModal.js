define(["jquery",
        "marionette",
        "underscore",
        "text!" + templateDir + "/modals/uploadModal.html",
        "backbone-bootstrap-modal"
    ],
    function ($, Marionette, _, uploadModal) {
        'use strict';
        /**
         * A class that handles display and rendering of the
         * upload data modal
         * @class UploadModal
         */

        var UploadModal = Marionette.ItemView.extend({
            id: 'upload-modal-wrapper',
            template: function (data) {
                return _.template(uploadModal, data);
            },
            ui: {
                modal: '#upload-modal'
            },
            initialize: function (opts) {
                this.app = opts.app;
                this.opts = opts;
                this.url = opts.url;
            },

            onRender: function() {
                this.ui.modal.on('hidden.bs.modal', this.cleanUp.bind(this));
            },

            serializeData: function(){
                return {
                  urlRoot: location.origin,
                  url: this.url
                };
            },

            cleanUp: function () {
                this.app.vent.trigger('refresh-collections');
            },

            showModal: function () {
                var iframe;
                this.ui.modal.modal();
                iframe = this.$el.find('iframe')[0];
                iframe.contentDocument.getElementById(this.app.activeProjectID).click();
            }



        });
        return UploadModal;
    });


