interface ToolbarScope extends ToolUIScope {
    toolbarCtrl: ToolbarCtrl;
}

/**
 * ToolbarCtrl is a controller that manages the list of buttons with which
 * different tools may be accessed. This controller concerns itself with
 * what happens when such a button is pressed.
 */
class ToolbarCtrl {
    static $inject = ['$scope', 'application', 'appstateService', 'authService'];

    tools: Tool[] = [];

    constructor(public $scope: ToolbarScope,
                private application: Application,
                private appstateService,
                private authService) {
        // Add the tools as soon as they are ready
        this.$scope.viewer.tools.then((tools) => {
            this.tools = tools;
        });
    }

    /**
     * This function is called when the Tool's button is pressed.
     */
    clickToolTab(tool: Tool) {
        this.$scope.toolUICtrl.toggleToolWindow(tool);
    }
}
angular.module('tmaps.ui').controller('ToolbarCtrl', ToolbarCtrl);
angular.module('tmaps.ui')
.directive('tmToolbar', function() {
    return {
        restrict: 'E',
        controller: 'ToolbarCtrl',
        controllerAs: 'toolbarCtrl',
        templateUrl: '/src/viewer/toolui/toolbar/tm-toolbar.html'
    };
});
