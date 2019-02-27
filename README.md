# Locations

[中文文档](https://github.com/TISUnion/Locations/blob/master/README_cn.md)

------
***This plugin follows GNU-3.0 license!***

Set waypoints and search them!

## Commandline Guide
* !!loc help - show help message
* !!loc add <unique name> <x> <y> <z> <nether: -1, overworld: 0, end: 1> - add a waypoint
  * the name shouldn't be add, del, help
  * tips: for convenience of search, you should use alias, fullname, and lower case only, like 'ironfarm/irongolemfarm/irontitan', but not 'IronFarm'
* !!loc add <unique name> here - add a waypoint in your position and dimension
* !!loc del <name> - delete waypoint, match whole word only
* !!loc <keyword> - returns all the waypoints containing <keyword>
* !!loc - list all the waypoints

You can click on any coordinate to teleport
