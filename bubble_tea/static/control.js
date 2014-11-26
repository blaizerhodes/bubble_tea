// FIXME: should wrap these in an app.. keeping namespace clean and all that. (no time now).
var btb = angular.module("bubbleTeaBonanza", ['ngCookies']); // etc.. 

// FIXME: handle failure to get and post!
// FIXME: get the tea options from the server once only (if we aren't already)!
// FIXME: I'm pretty sure I've screwed the pooch with the angularjs event model here :(

// apparently this is the fastest way to get a deep copy in javascript!
clone = function(obj) {
    return angular.fromJson(angular.toJson(obj));
}


function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) != -1) return c.substring(name.length,c.length);
    }
    return "";
} 
//         {{ cookies["customer_key"] }}


// This is the client side model for the customers order.
function orderController($scope, $rootScope, $http) {

    // globals 
    $rootScope.customer = null;
    $rootScope.currentTeaOrder = new TeaOrder();
    $rootScope.teaOrders = [$rootScope.currentTeaOrder ];
    $rootScope.selectedTeaPrice = 0; // for the current tea
    $rootScope.totalPrice = 0;       // for the whole order 
    
    // we need the tea toppings early on (and just the once)
    if (!$rootScope.getting_toppings) {
        $rootScope.getting_toppings = true;
        $http.get("get_tea_toppings").success(
            function(response) {
                toppings = response;
                for (i in toppings) {
                    topping = toppings[i];
                    topping.checked = false;
                    $rootScope.currentTeaOrder.teaToppings.push(topping);
                }
                $rootScope.updatePrices();                    
            }
        );
    }
    
    $rootScope.orderAnotherTea = function() {
        // create a new tea order
        tea = new TeaOrder();
        tea.teaType = $rootScope.currentTeaOrder.teaType;
        tea.teaFlavour = $rootScope.currentTeaOrder.teaFlavour;        
        // deep copy here! (we want diffferent checked states for each tea order)
        tea.teaToppings = clone($rootScope.currentTeaOrder.teaToppings); 
        tea.teaSize = $rootScope.currentTeaOrder.teaSize;
        $rootScope.currentTeaOrder = tea;

        // and push it on the list
        $rootScope.teaOrders.push($rootScope.currentTeaOrder);
        $rootScope.updatePrices();        
    };

    //
    // change handlers for the various widgets..
    //
    $rootScope.updateSelectedTeaType = function(newSelectedTeaType) {
        // we need this so the select widget gets updated correctly 
        $scope.currentTeaOrder.teaType = newSelectedTeaType; 
        $rootScope.updatePrices();
    };

    $rootScope.updateSelectedTeaFlavour = function(newSelectedTeaFlavour) {
        // we need this so the select widget gets updated correctly 
        $rootScope.currentTeaOrder.teaFlavour = newSelectedTeaFlavour;
        $rootScope.updatePrices();
    };

    // called whenever the topping selections for the current tea order is modified
    $rootScope.updateSelectedToppings = function(topping) {
        $rootScope.updatePrices();
    };

    $rootScope.updateSelectedTeaSize = function(selectedTeaSize) {
        // we need this so the radio widget gets updated correctly 
        $rootScope.currentTeaOrder.teaSize = selectedTeaSize; 
        $rootScope.updatePrices();
    };

    $rootScope.updatePrices = function() {
        // updates the prices for the current tea 
        // FIXME: placeholder logic here...
        var teaPrice = 0;
        var tea = $rootScope.currentTeaOrder;

        // don't calculate the prices until we've got relevent pricing info from the server.
        if (tea.teaType && tea.teaFlavour && tea.teaToppings && tea.teaSize) { 
            
            // calculate the cost of all the toppings
            var toppingPrice = 0;
            var badTopping = false;
            for (i in tea.teaToppings) {
                topping = tea.teaToppings[i];
                if (!topping.checked) {
                    continue;
                }
                else if (!topping.additional_cost) {
                    badTopping = true;         
                    // FIXME: FAIL FASTER AND MORE VISIBLEY HERE!
                    break;
                }
                else {
                    toppingPrice += topping.additional_cost;
                }
            }

            // if we have a bad topping bail!
            if (!badTopping) {                                         
                teaPrice = 
                    tea.teaType.cost +
                    tea.teaFlavour.additional_cost + 
                    tea.teaSize.additional_cost +
                    toppingPrice;
            }
        }            
        $rootScope.currentTeaOrder.teaPrice = teaPrice;

        // add up all the tea prices to get the total price
        totalPrice = 0;
        for (i in $rootScope.teaOrders) {
            teaOrder = $rootScope.teaOrders[i];
            totalPrice += teaOrder.teaPrice;
        }
        $rootScope.totalPrice = totalPrice;            
    };

    // removes a tea order from the list of teaOrders (surprise!)
    $rootScope.deleteTeaOrder = function(teaOrder) {
        // never delete the current tea (UI shouldn't let this happen).
        if (teaOrder !== $rootScope.currentTeaOrder) {
            var index = $rootScope.teaOrders.indexOf(teaOrder);
            if (index > -1) {
                $rootScope.teaOrders.splice(index, 1);
            }            
        }       
    };

    // makes the edit tea order the current tea order
    $rootScope.editTeaOrder = function(teaOrder) {
        $rootScope.currentTeaOrder = teaOrder;
    };

    // register the order with the server!!!  order some tea!
    $rootScope.placeOrder = function() {
        order_msg = {customer_key: getCookie("customer_key"), 
                     order: $rootScope.teaOrders,
                     // cost sent to double check.. don't trust the client                     
                     total_cost: $rootScope.totalPrice}; 
        order_msg_json = angular.toJson(order_msg);
        $http.post("place_order", order_msg_json).success(
            function(response) {
                alert("Order Placed" + response);
                // FIXME.. UI should do something nice here.. blaize is out of time :(
            }
        );        
    };

    $scope.go_to_login = function() {
        window.location.pathname = '/login';
    }

    // logout 
    $scope.do_logout = function() {
        document.cookie = "username=; expires=Thu, 01 Jan 1970 00:00:00 UTC"; 
        document.cookie = "customer_key=; expires=Thu, 01 Jan 1970 00:00:00 UTC"; 
    }

    $scope.is_logged_in = function() {
        var username = getCookie("customer_key");
        return username != "";
    };

    $scope.get_username = function() {
        return getCookie("username");
    };

}



function loginController($scope, $http) {
    $scope.do_login = function(username, password) {
        login_details_json = {username: username, password: password};
        $http.post("do_login", login_details_json).success(
            function(response) {
                document.cookie="username=" + response["username"];
                document.cookie="customer_key=" + response["key"];
                window.location.href = "/";
            }
        );
    } 
} 



// tea order data struct (one per tea)
function TeaOrder () {
    this.teaType = "-";
    this.teaFlavour = "-";
    this.teaToppings = [];
    this.teaSize = "-";
    this.teaPrice = 0;
}


function teaTypeController($scope, $rootScope, $http) {
    $http.get("get_tea_types").success(
        function(response) {
            $scope.tea_types = response;
            $rootScope.updateSelectedTeaType($scope.tea_types[0]);
        }
    );
} 

function teaFlavourController($scope, $rootScope, $http) {
    $http.get("get_tea_flavours").success(
        function(response) {
             $scope.flavours = response;
             $rootScope.updateSelectedTeaFlavour($scope.flavours[0]);            
         }
    );
} 

function teaSizeController($scope, $rootScope, $http) {
    $http.get("get_tea_sizes").success(
        function(response) {
            $scope.teaSizes = response;
            // set to medium (FIXME HACK: all the defaults should be setable in the db)
            $rootScope.updateSelectedTeaSize($scope.teaSizes[1]); 
        }
    );
}

function customerController($scope) {
    $scope.username = "blaize";
    $scope.password = "Doe";
}





