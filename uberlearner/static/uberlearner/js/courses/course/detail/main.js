require([
    'ko',
    'jquery',
    'uberlearner/js/courses/course/detail/viewmodel',
    'uberlearner/js/utils/messages/viewmodel',
    'bootstrap'
], function(ko, $, ViewModel) {
    $(function() {
        ko.applyBindings(new ViewModel(), $('#course-detail-block')[0]);
    });
});