/* found on https://www.cg.tuwien.ac.at/courses/Visualisierung2/HallOfFame/2014/Tofi/Homepage/codedoc/files/client.js.html */

/**
 * Client module
 *
 * @module client
 */

/**
 * The client file
 *
 * @class Client
 */

$(document).ready(function () {

"use strict";

  // connect to server
  var socket = io.connect("http://localhost");
  var REL_SPOUSE = 1; // enum
  var REL_CHILD = 2; // enum
  var canvas = document.getElementById("timenet_canvas");
  var WIDTH = Math.floor($(window).width() * 0.9); // canvas width
  WIDTH -= WIDTH % 2; // make even
  var HEIGHT = 300; // canvas default height
  var LINE_THICKNESS = 12; // line thickness
  var FEMALE_COLOR = "#bb4444";
  var MALE_COLOR = "#4444dd";
  var LIGHTNESS_VISIBLE = 0.75; // color for visible but unselected line
  var DROPLINE_THICKNESS = 2;
  var DROPLINE_COLOR = "#555";
  var DROPLINE_FADE_LENGTH = 50; // how much of a dropline should be visible before it fades out
  var SPACING = LINE_THICKNESS / 2 + 5; // space between lines
  var DEFAULT_CURVE_HEIGHT = 25;
  var CURVE_FACTOR = 0.6; // determines how a relationship curve will look
  var RELATION_CURVE_LENGTH = WIDTH / 20;
  var MIN_RELATION_CURVE_LENGTH = 10; // if a relationship is too short, the curve should have a minimum length
  var RELATION_SPACING = 2; // space between curves in a relationship
  var DOI_MAX = 10; // doi of selected line
  var ALPHA_INVISIBLE;
  var ALPHA_INVISIBLE_VISIBLE = 0.1; // opacity of invisible objects (when checked)
  var LINE_ANIM_SPEED = 600; // speed of animation
  var FONT = "Tahoma, Geneva, sans-serif";

  var TIMELINE_COLOR = "#ccc";
  var TIMELINE_TEXT_COLOR = "#999";

  paper.setup(canvas);

  canvas.width = WIDTH;
  canvas.height = HEIGHT;
  $("#doi_max").text(DOI_MAX);

  /**
   * @method arrayDiff
   * @param {Array} a
   * @param {Array} b
   * @return a without the objects of b
   * @for Client
   */
  function arrayDiff(a, b) {
    return a.filter(function(i) {return b.indexOf(i) < 0;});
  }

  /**
   * A local block in the layout (conjugally related persons)
   *
   * @class Block
   * @constructor
   * @param {Array} relationships
   * @param {Array} persons
   * @param {Array} children
   */
  function Block(relationships, persons, children) {
    this.relationships = relationships;
    this.persons = persons;
    this.children = children;
  }

  /**
   * Relationship in a person's life
   *
   * @class EventRelationship
   * @constructor
   * @param {Number} startX
   * @param {Number} endX
   * @param {Number} otherPersonId
   */
  function EventRelationship(startX, endX, otherPersonId) {
    this.startX = startX;
    this.endX = endX;
    this.otherPersonId = otherPersonId;
  }

  /**
   * Start and end of a person's life
   *
   * @class EventExistence
   * @constructor
   * @param {Number} startX
   * @param {Number} endX
   */
  function EventExistence(startX, endX) {
    this.startX = startX;
    this.endX = endX;
  }

  /**
   * Annotation at a point in a person's life
   *
   * @class EventAnnotation
   * @constructor
   * @param {Number} X
   * @param {String} title
   * @param {String} text
   * @param {Date} date
   */
  function EventAnnotation(X,title, text, date){
    this.x = X;
    this.title = title;
    this.text = text;
    this.date = date;
  }

  /**
   * Compare numbers for sorting
   *
   * @method cmpNumbers
   * @param {Number} a
   * @param {Number} b
   * @return {Number}
   * @for Client
   */
  function cmpNumbers(a, b) {
    return a - b;
  }

  /**
   * Compare events for sorting
   *
   * @method cmpEvents
   * @param {Event} a
   * @param {Event} b
   * @return {Number}
   * @for Client
   */
  function cmpEvents(a, b) {
    return a.startX - b.startX;
  }

  /**
   * Compare dates for sorting
   *
   * @method cmpDates
   * @param {Date} a
   * @param {Date} b
   * @return {Number}
   * @for Client
   */
  function cmpDates(a, b) {
    return a.getTime() - b.getTime();
  }

  /**
   * Compare birth dates of persons for sorting
   *
   * @method cmpBirthDates
   * @param {Person} a
   * @param {Person} b
   * @return {Number}
   * @for Client
   */
  function cmpBirthDates(a, b) {
    return cmpDates(a.dateOfBirth, b.dateOfBirth);
  }

  /**
   * Copy an object
   *
   * @method copyObject
   * @param {Object} o
   * @return {Object}
   * @for Client
   */
  function copyObject(o) {
    return $.extend(true, {}, o);
  }

  /**
   * Copy an array (copy every object in the array)
   *
   * @method copyArray
   * @param {Array} a
   * @return {Array}
   * @for Client
   */
  function copyArray(a) {
    var r = [];
    a.forEach(function (o) {
      if (o === null || o === undefined) {
        r.push(o);
      } else {
        r.push(copyObject(o));
      }
    });
    return r;
  }

  /**
   * Sign function
   *
   * @method sign
   * @param {Number} x
   * @return {Number}
   * @for Client
   */
  function sign(x) {
    return x > 0 ? 1 : x < 0 ? -1 : 0;
  }

  /**
   * @method otherPersonId
   * @param {Person} p
   * @param {Relationship} rel
   * @return {Number} id of other person in the relationship
   * @for Client
   */
  function otherPersonId(p, rel) {
    if (rel.person1Id === p.id) {
      return rel.person2Id;
    } else {
      return rel.person1Id;
    }
  }

  /**
   * Called when information about available timenets is received from the server
   *
   * @event timenet_list
   * @param data contains the list of timenet ids
   */
  socket.on("timenet_list", function (data) {
    $("#combo_timenets").empty();
    data.timenets.forEach(function (tn) {
      $("<option/>").val(parseInt(tn.id, 10)).text(tn.name).appendTo("#combo_timenets");
    });
  });

  /**
   * Called when database data is received
   *
   * @event db_data
   * @param data contains the database content from the server
   */
  socket.on("db_data", function (data) {
    var persons = [];
    var relationships = [];
    var annotations = [];
    var localBlocks = [];
    var range = 0;
    var y; // current y while drawing
    var i = 0; // person position index
    var firstBirth = null;
    var lastDeath = null;
    var firstBlock;
    var sortedBlocks = [];
    var isDefaultDois = false;
    var DOI_CONJUGAL_RATE = parseInt($("#doi_conjugal_rate").val(), 10);
    var DOI_CHILD_RATE = parseInt($("#doi_child_rate").val(), 10);

    /**
     * Contains data for the current animation
     *
     * @class LineAnim
     * @constructor
     * @param {Boolean} active
     * @param {paper.Path} path
     * @param {Number} from
     * @param {Number} to
     * @param {Number} total
     * @param {Number} sign
     */
    var lineAnim = {
      active: false,
      path: null,
      from: null,
      to: null,
      total: 0,
      sign: 1
    };

    if (data.persons.length === 0) {
      return;
    }

    if (isNaN(DOI_CHILD_RATE) || !$.isNumeric(DOI_CHILD_RATE)) {
      DOI_CHILD_RATE = 8;
    }

    if (isNaN(DOI_CONJUGAL_RATE) || !$.isNumeric(DOI_CONJUGAL_RATE)) {
      DOI_CONJUGAL_RATE = 1;
    }

    /**
     * Draws a curve for the current path to endPoint (used in fullRelationCurveTo)
     *
     * @method relationCurveTo
     * @param {paper.Path} path
     * @param {paper.Point} endPoint
     * @for Client
     */
    function relationCurveTo(path, endPoint) {
      var startPoint = path.lastSegment.point;
      var offset = CURVE_FACTOR * (endPoint.x - startPoint.x);
      path.cubicCurveTo(new paper.Point(startPoint.x + offset, startPoint.y),
        new paper.Point(endPoint.x - offset, endPoint.y),
        new paper.Point(endPoint.x, endPoint.y));
    }

    /**
     * Draws a "full relation curve", meaning two curves that are
     * connected by a straight line
     *
     * @method fullRelationCurveTo
     * @param {paper.Path} path
     * @param {paper.Point} endPoint
     * @param {Number} curveHeight
     * @for Client
     */
    function fullRelationCurveTo(path, endPoint, curveHeight) {
      var startPoint = path.lastSegment.point;
      var delta = endPoint.x - startPoint.x;
      var curveLength = RELATION_CURVE_LENGTH;
      if (delta <= RELATION_CURVE_LENGTH * 2) {
        curveLength = delta / 2;
        relationCurveTo(path, new paper.Point(startPoint.x + curveLength, y + curveHeight));
        relationCurveTo(path, new paper.Point(endPoint.x, y));
      } else {
        relationCurveTo(path, new paper.Point(startPoint.x + curveLength, y + curveHeight));
        path.lineTo(startPoint.x + delta - curveLength, y + curveHeight);
        relationCurveTo(path, new paper.Point(endPoint.x, y));
      }

      return curveLength;
    }

    /**
     * @method getX
     * @param {Date} date
     * @return {Number} x-position on screen for date
     * @for Client
     */
    function getX(date) {
      var d;
      if (typeof date.getTime === "function") { // date is a Date
        d = date.getTime();
      } else { // date is a number
        d = date;
      }
      return (d + Math.abs(firstBirth.getTime())) / range * WIDTH;
    }

    /**
     * @method personColor
     * @param {Person} person
     * @return {paper.Color} color of person's line, determined by doi and sex
     * @for Client
     */
    function personColor(person) {
      var color;
      if (person.sex === "f") {
        color = new paper.Color(FEMALE_COLOR);
      } else if (person.sex === "m") {
        color = new paper.Color(MALE_COLOR);
      }

      if (person.doi < DOI_MAX && person.doi > 0) {
        color.lightness = LIGHTNESS_VISIBLE;
      }

      return color;
    }

    /**
     * Insert conjugal relationship and the involved persons into the block;
     * then go to their other conjugal relationships, add them to the block,
     * ... and so on, until the block is completed.
     *
     * @method fillBlock
     * @param {Number} relId
     * @param {Block} block
     * @for Client
     */
    function fillBlock(relId, block) {
      if (data.relationships[relId] === undefined || data.relationships[relId] === null) {
        return;
      }

      var rel = relationships[relId];
      delete data.relationships[relId];

      var person1 = persons[rel.person1Id];
      var person2 = persons[rel.person2Id];
      delete data.persons[rel.person1Id];
      delete data.persons[rel.person2Id];

      [person1, person2].forEach(function (p) {
        if (block.persons.indexOf(p) === -1) {
          // add person to block
          block.persons.push(p);
          // add children to block
          p.childRelationships.forEach(function (childRelId) {
            var currentParentId = relationships[childRelId].person2Id;
            var currentChildId = relationships[childRelId].person1Id;
            if (p.id === currentParentId) {
              block.children.push(currentChildId);
            }
          });
          p.block = block;
        }

        p.conjugalRelationships.forEach(function (pRelId) {
          fillBlock(pRelId, block);
        });
      });
    }

    /**
     * Set doi values of all persons to value
     *
     * @method resetDois
     * @param {Number} value
     * @for Client
     */
    function resetDois(value) {
      persons.forEach(function (person) {
        if (person === undefined || person === null) {
          return;
        }
        person.doi = value;
      });
    }

    console.log("received data");

    // repair the data, especially dates
    data.persons.forEach(function (p) {
      if (p === null) {
        return;
      }
      p.dateOfBirth = new Date(p.dateOfBirth);
      p.dateOfDeath = new Date(p.dateOfDeath);
    });
    data.relationships.forEach(function (r) {
      if (r === null) {
        return;
      }
      r.startDate = new Date(r.startDate);
      r.endDate = new Date(r.endDate);
    });
    data.annotations.forEach(function (a){
      if (a === null){
        return;
      }
      a.date = new Date(a.date);
    });

    // copy data from received data object to client-internal arrays
    persons = copyArray(data.persons);
    relationships = copyArray(data.relationships);
    annotations = copyArray(data.annotations);

    resetDois(DOI_MAX);
    isDefaultDois = true;

    /**
     * Generate blocks of relationships
     *
     * @method * generate blocks
     * @for Client
     */
    (function () {
      for (var i = 0; i < data.relationships.length; ++i) {
        if (data.relationships[i] === undefined || data.relationships[i] === null) {
          continue;
        }
        if (data.relationships[i].type === REL_SPOUSE) {
          var block = new Block([data.relationships[i]], [], []);
          fillBlock(i, block);

          // remove duplicate block child ids
          block.children = block.children.filter(function (value, index, self) {
            return self.indexOf(value) === index;
          });

          block.children.sort(function (a, b) {
            return -cmpBirthDates(persons[a], persons[b]);
          });

          console.log("new block size: " + block.persons.length, "children: ", JSON.stringify(block.children));
          localBlocks.push(block);
        }
      }
    })();

    /**
     * Generate 1-person-blocks for persons without relationships,
     * preprocess data
     *
     * @method * generate 1-person-blocks
     * @for Client
     */
    persons.forEach(function (p) {
      if (p === null || p === undefined) {
        return;
      }

      // create blocks for singles
      if (p.conjugalRelationships.length === 0) {
        var block = new Block([], [p], []);
        localBlocks.push(block);
        p.block = block;
      }

      // sort child relationships
      p.childRelationships.sort(function (a, b) {
        return cmpDates(relationships[a].startDate, relationships[b].startDate);
      });
    });

    // Find first block to draw: the one with the earliest child birth
    (function () {
      var earliest = {child: -1, block: -1};
      localBlocks.forEach(function (block) {
        if (block.children.length === 0) {
          return;
        }

        var earliestInBlock = block.children[block.children.length - 1];
        if (earliest.child === -1 || earliest.parent === -1 || cmpBirthDates(persons[earliestInBlock], persons[earliest.child]) < 0) {
          earliest.child = earliestInBlock;
          earliest.block = block;
        }
      });
      firstBlock = earliest.block;
    })();

    /**
     * Sort the persons of a block by birth date
     *
     * @method sortBlockPersons
     * @for Client
     */
    function sortBlockPersons() {
      // sort persons in each block by birth date
      localBlocks.forEach(function (block) {
        block.persons.sort(cmpBirthDates);
      });
    }
    sortBlockPersons();

    // sort blocks by earliest birth date
    localBlocks.sort(function (a, b) {
      if (a.persons.length > 0 && b.persons.length > 0) {
        return a.persons[0].dateOfBirth.getTime() - b.persons[0].dateOfBirth.getTime();
      } else if (a.persons.length > 0) {
        return 1;
      } else {
        return -1;
      }
    });

    // get min and max dates of all persons
    persons.forEach(function (person) {
      if (person === null) {
        return;
      }

      if (firstBirth === null || person.dateOfBirth.getTime() < firstBirth.getTime()) {
        firstBirth = person.dateOfBirth;
      }
      if (lastDeath === null || lastDeath.getTime() < person.dateOfDeath.getTime()) {
        lastDeath = person.dateOfDeath;
      }
    });
    range = lastDeath.getTime() - firstBirth.getTime();

    /**
     * Determine the block order (global layout)
     *
     * @method * sort blocks
     * @for Client
     */
    (function () {
      function addChildBlock(childId) {
        if (sortedBlocks.indexOf(persons[childId].block) === -1) {
          sortedBlocks.push(persons[childId].block);
        }

        if (persons[childId].childRelationships.length < 0) {
          return;
        }

        persons[childId].block.children.forEach(function (subChildId) {
          addChildBlock(subChildId);
        });
      }

      function addBlocks(list) {
        list.forEach(function (currentBlock) {
          if (sortedBlocks.indexOf(currentBlock) === -1) {
            sortedBlocks.push(currentBlock);
          }
          currentBlock.children.forEach(function (childId) {
            addChildBlock(childId);
          });

          if (sortedBlocks.length === localBlocks.length) {
            return;
          }
          addBlocks(arrayDiff(localBlocks, sortedBlocks));
        });
      }
      addBlocks([firstBlock]);
    })();

    /**
     * As the name says. Must be called every time the layout changes
     *
     * @method drawEverything
     * @for Client
     */
    function drawEverything() {
      // clear everything
      paper.project.clear();
      canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);

      y = SPACING*4;

      if ($("#show_invisible_check").prop("checked")) {
        ALPHA_INVISIBLE = ALPHA_INVISIBLE_VISIBLE;
      } else {
        ALPHA_INVISIBLE = 0;
      }

      sortedBlocks.forEach(function (block) {

        /**
         *Sorts a persons Life into chronological events and assigns them canvas coordinates.
         *
         * @method * parse a persons Life into Events
         * @param {Person} person  a person of a block
         * @for Client
         */
        block.persons.forEach(function (person) {
          if (person === null) {
            return;
          }

          var startX = getX(person.dateOfBirth);
          var endX = getX(person.dateOfDeath);

          person.lifeline = [new EventExistence(startX, endX)];
          person.hasRelationshipUp = false;
          person.hasRelationshipDown = false;
          person.position = i;
          i++;

          person.conjugalRelationships.sort(function (a, b) {
            return relationships[a].startDate.getTime() - relationships[b].startDate.getTime();
          });

          person.conjugalRelationships.forEach(function (relId) {
            var rel = relationships[relId];
            var otherPersonId;
            if (person.id === rel.person1Id) {
              otherPersonId = rel.person2Id;
            } else {
              otherPersonId = rel.person1Id;
            }
            var event = new EventRelationship(getX(rel.startDate.getTime()), getX(rel.endDate.getTime()), otherPersonId);
            person.lifeline.push(event);
          });
          person.annotations.forEach(function(annoId){
            var anno = annotations[annoId]
            var event = new EventAnnotation(getX(anno.date.getTime()), anno.title, anno.text, anno.date);
            person.lifeline.push(event);
          });

          person.lifeline.sort(cmpEvents);
          //var rel = relationships[person.conjugalRelationships[0]];
        });

        // draw lines
        /**
         *Draws Lifelines of a Block
         *
         * @method *draw persons of a block
         * @param {Person} a person in the block Person
         * @for Client
         */
        block.persons.forEach(function (person) {
          var path = new paper.Path();
          var vSpacing = SPACING;
          var startX;
          var deathX;
          var curveHeight = DEFAULT_CURVE_HEIGHT;
          var orientation;
          var otherPerson;
          var parentPath = {first: null, second: null};
          var backgroundPath;
          function stopColor(alpha) {
            var c = new Color(path.strokeColor);
            c.lightness = LIGHTNESS_VISIBLE;
            c.alpha = alpha;
            return c;
          }

          function doiAlpha(doi) {
            if (doi <= 0 || doi === DOI_MAX + 1) {
              return ALPHA_INVISIBLE;
            } else  {
              return 1;
            }

          }

          path.strokeColor = personColor(person);

          if (person.hasRelationshipUp) {
            y += DEFAULT_CURVE_HEIGHT;
            vSpacing += SPACING;
          }
          if (person.hasRelationshipDown) {
            vSpacing += DEFAULT_CURVE_HEIGHT + SPACING;
          }
          vSpacing = DEFAULT_CURVE_HEIGHT * 2 + SPACING * 2;
          /**
           *Draws a person's lifeLine from event to event
           *
           * @method * Draw LifeLines
           * @param {event} event Event in a persons Life
           * @param {Number} currentDoi maximal DOI value
           * @for Client
           */
          person.lifeline.forEach(function (event) {
            if (event instanceof EventExistence) {
              startX = event.startX;
              path.moveTo(startX, y);
              deathX = event.endX;

              // find parent y
              var parents = [];
              person.childRelationships.forEach(function (relId) {
                if (relationships[relId].person1Id === person.id) {
                  parents.push(relationships[relId].person2Id);
                }
              });
              if (parents.length >= 2) {
                parentPath.first = persons[parents[0]].path;
                parentPath.second = persons[parents[1]].path;
              }
              /**
               *Writes a person's name and DOI value on their lifeline
               *
               * @method *write text on LifeLine
               * @for Client
               */
              (function() {
                //print Text in lifeline
                var textColor = new paper.Color(1);
                textColor.alpha = doiAlpha(person.doi);
                var textLifeLineStyle = {
                  fillColor: textColor,
                  font: FONT,
                  fontSize: (LINE_THICKNESS*0.8),
                  shadowColor: "black",
                  shadowBlur: 1,
                  shadowOffset: new paper.Point(1, 0),
                  fontWeight: "bold"
                };
                var textLifeLineName = new paper.PointText(new paper.Point(startX+2,y+LINE_THICKNESS *0.3));
                textLifeLineName.content = person.name;
                textLifeLineName.style = textLifeLineStyle;

                var textLifeLineDoi = new paper.PointText(new paper.Point(deathX, y+LINE_THICKNESS *0.3));
                textLifeLineDoi.content = person.doi;
                textLifeLineDoi.position.x -=  (textLifeLineDoi.bounds.width +3);
                textLifeLineDoi.style= textLifeLineStyle;
                if (!$("#show_invisible_check").prop("checked")) {
                  textLifeLineDoi.visible = false;
                }
                person.textName = textLifeLineName;
                person.textDoi = textLifeLineDoi;
              })();
            } else if (event instanceof EventRelationship) {
              otherPerson = persons[event.otherPersonId];

              if (otherPerson.position < person.position) {
                orientation = -1;
                curveHeight = -(y - otherPerson.positionY) + DEFAULT_CURVE_HEIGHT + LINE_THICKNESS + RELATION_SPACING;
              } else {
                orientation = 1;
                curveHeight = orientation * DEFAULT_CURVE_HEIGHT;
              }

              path.lineTo(event.startX, y);
              event.curveLength = fullRelationCurveTo(path, new paper.Point(event.endX, y), curveHeight);
            }
          });

          path.lineTo(deathX, y);
          /**
           * Draws a Star on a persons Lifeline, if a special event happened in a persons life.
           *
           * @method *drawAnnotationSymbol
           * @param {Event} EventAnnotation of a person
           * @for Client
           */
          person.lifeline.forEach(function (event){
            if (event instanceof EventAnnotation) {
              var intersectionPath = new paper.Path.Line(new paper.Point(event.x, 0), new paper.Point(event.x,y+ DEFAULT_CURVE_HEIGHT));
              var starY = intersectionPath.getIntersections(path)[0].point.y;
              var star = new paper.Path.Star(new paper.Point(event.x,starY), 5,5, 10);
              star.shadowColor = "black";
              star.shadowBlur = 13;
              star.shadowOffset = new paper.Point(1,1);
              star.fillColor = 'yellow';
              star.fillColor.alpha = doiAlpha(person.doi);
              star.data = event;
            }
          });
          /**
           *Draws droplines from parents to children, handels different visibility cases between involved people, and fades lines accordingly.
           *
           * @method *drawDropLines
           * @for Client
           */
          // draw drop line
          (function () {
            var dPath;
            var marker;
            var marker2;
            var gradientStops;
            var lineLength;
            var upperParentPath;
            var lowerParentPath;
            var upperParentAlpha;
            var lowerParentAlpha;
            var personAlpha;

            function dStopColor(alpha) {
              var c = dPath.strokeColor.clone();
              c.alpha = alpha;
              return c;
            }

            // draw drop line
            if (parentPath.first !== null && parentPath.second !== null) {
              dPath = new paper.Path();

              dPath.moveTo(startX, y);
              dPath.lineTo(startX, 0);
              parentPath.first.y = parentPath.first.getIntersections(dPath)[0].point.y;
              parentPath.second.y = parentPath.second.getIntersections(dPath)[0].point.y;
              dPath.removeSegments();

              if (parentPath.first.y < parentPath.second.y) {
                upperParentPath = parentPath.first;
                lowerParentPath = parentPath.second;
              } else {
                upperParentPath = parentPath.second;
                lowerParentPath = parentPath.first;
              }
              upperParentAlpha = doiAlpha(persons[upperParentPath.data.id].doi);
              lowerParentAlpha = doiAlpha(persons[lowerParentPath.data.id].doi);
              personAlpha = doiAlpha(person.doi);

              dPath.strokeColor = DROPLINE_COLOR;
              dPath.strokeWidth = DROPLINE_THICKNESS;
              dPath.dashArray = [2, 2];
              dPath.moveTo(startX, y);
              marker = paper.Shape.Circle(new paper.Point(100, 100), 3);
              marker.fillColor = "#000000";

              lineLength = Math.min(DROPLINE_FADE_LENGTH, dPath.firstSegment.point.y - Math.max(upperParentPath.y, lowerParentPath.y) / 2);

              gradientStops = [new paper.GradientStop(dStopColor(personAlpha), 0)];

              // parents are in relationship, only 1 marker
              if (Math.abs(parentPath.first.y - parentPath.second.y) === LINE_THICKNESS + RELATION_SPACING) {
                var parentY = Math.min(parentPath.first.y, parentPath.second.y) + (LINE_THICKNESS + RELATION_SPACING) * 0.5;
                dPath.lineTo(startX, parentY);
                marker.position = new paper.Point(startX, parentY);

                // if both parents are invisible
                if (upperParentAlpha === ALPHA_INVISIBLE &&
                  lowerParentAlpha === ALPHA_INVISIBLE) {

                  marker.fillColor.alpha = ALPHA_INVISIBLE;

                  gradientStops.push(new paper.GradientStop(dStopColor(ALPHA_INVISIBLE), lineLength / dPath.length));
                  gradientStops.push(new paper.GradientStop(dStopColor(ALPHA_INVISIBLE), 1));
                } else {
                  marker.fillColor.alpha = dStopColor(1);

                  gradientStops.push(new paper.GradientStop(dStopColor(personAlpha), 1 - lineLength / dPath.length));
                  gradientStops.push(new paper.GradientStop(dStopColor(1), 1));
                }
              } else { // separate parents
                marker.position = new paper.Point(startX, upperParentPath.y);
                marker2 = marker.clone();
                marker2.position = new paper.Point(startX, lowerParentPath.y);
                dPath.lineTo(startX, marker.position.y);

                // if both parents are invisible
                if (upperParentAlpha === ALPHA_INVISIBLE &&
                  lowerParentAlpha === ALPHA_INVISIBLE) {

                  marker.fillColor.alpha = ALPHA_INVISIBLE;
                  marker2.fillColor.alpha = ALPHA_INVISIBLE;

                  gradientStops.push(new paper.GradientStop(dStopColor(ALPHA_INVISIBLE), lineLength / dPath.length));
                  gradientStops.push(new paper.GradientStop(dStopColor(ALPHA_INVISIBLE), 1));
                } else if (upperParentAlpha !== ALPHA_INVISIBLE) { // upper parent visible
                  marker.fillColor.alpha = upperParentAlpha;
                  if (personAlpha === ALPHA_INVISIBLE && lowerParentAlpha === ALPHA_INVISIBLE) {
                    marker2.fillColor.alpha = lowerParentAlpha;
                    gradientStops.push(new paper.GradientStop(dStopColor(ALPHA_INVISIBLE), 1 - lineLength / dPath.length));
                  } else {
                    marker2.fillColor.alpha = upperParentAlpha; // visible, event if line is invisible
                    if (personAlpha === ALPHA_INVISIBLE) {
                      gradientStops.push(new paper.GradientStop(dStopColor(ALPHA_INVISIBLE), 1 - (Math.abs(upperParentPath.y - lowerParentPath.y) + lineLength) / dPath.length));
                    }
                    gradientStops.push(new paper.GradientStop(dStopColor(1), 1 - Math.abs(upperParentPath.y - lowerParentPath.y) / dPath.length));
                  }
                  gradientStops.push(new paper.GradientStop(dStopColor(upperParentAlpha), 1));
                } else if (lowerParentAlpha !== ALPHA_INVISIBLE) { // upper parent invisible, lower parent visible
                  marker.fillColor.alpha = upperParentAlpha;
                  marker2.fillColor.alpha = lowerParentAlpha;
                  if (personAlpha === ALPHA_INVISIBLE) {
                    gradientStops.push(new paper.GradientStop(dStopColor(ALPHA_INVISIBLE), 1 - (Math.abs(upperParentPath.y - lowerParentPath.y) + lineLength) / dPath.length));
                  }
                  gradientStops.push(new paper.GradientStop(dStopColor(1), 1 - Math.abs(upperParentPath.y - lowerParentPath.y) / dPath.length));
                  gradientStops.push(new paper.GradientStop(dStopColor(ALPHA_INVISIBLE), 1 - (Math.abs(upperParentPath.y - lowerParentPath.y) - lineLength) / dPath.length));
                  gradientStops.push(new paper.GradientStop(dStopColor(ALPHA_INVISIBLE), 1));
                }
              }

              dPath.strokeColor = {
                gradient: {
                  stops: gradientStops
                },
                origin: dPath.firstSegment.point,
                destination: dPath.lastSegment.point
              };
            }
          })();

          // doi
          path.strokeColor.alpha = doiAlpha(person.doi);
          path.strokeWidth = LINE_THICKNESS;
          /**
           *Fades in invisible Lifelines if the unimportant persons is in a relationship with a more important person.
           *
           * @method *fadeInLifeLines
           * @for Client
           */
          // faded lines
          if (person.doi <= 0 && person.conjugalRelationships.length > 0) (function () {
            var lineLength = deathX - startX;
            var gradientStops = [new paper.GradientStop(stopColor(ALPHA_INVISIBLE), 0)];

            person.lifeline.forEach(function (event) {
              if (event instanceof EventRelationship && persons[event.otherPersonId].doi > 0
                && persons[event.otherPersonId].doi !== DOI_MAX + 1) {

                var startRel = (event.startX - startX) / lineLength;
                var endRel = (event.endX - startX) / lineLength;
                var otherAlpha = doiAlpha(persons[event.otherPersonId].doi);

                if (event.curveLength < RELATION_CURVE_LENGTH) {
                  startRel = (event.startX - MIN_RELATION_CURVE_LENGTH - startX) / lineLength;
                  endRel = (event.endX + MIN_RELATION_CURVE_LENGTH - startX) / lineLength;
                }

                gradientStops.push(new paper.GradientStop(stopColor(ALPHA_INVISIBLE), startRel));
                gradientStops.push(new paper.GradientStop(stopColor(otherAlpha), (event.startX - startX + event.curveLength / 2) / lineLength));
                gradientStops.push(new paper.GradientStop(stopColor(otherAlpha), (event.endX - startX - event.curveLength / 2) / lineLength));
                gradientStops.push(new paper.GradientStop(stopColor(ALPHA_INVISIBLE), endRel));
              }
            });
            gradientStops.push(new paper.GradientStop(stopColor(ALPHA_INVISIBLE), 1));

            path.strokeColor = {
              gradient: {
                stops: gradientStops
              },
              origin: new paper.Point(startX, y),
              destination: new paper.Point(deathX, y)
            };
          })();

          person.vSpacing = vSpacing;
          person.positionY = y;
          y += vSpacing;
          path.data = { id: person.id };
          person.path = path.clone();

          path.visible = false;

          // set background path (border)
          //if (person.doi > 0 && person.doi != DOI_MAX + 1) {
          if (!isDefaultDois && person.doi === DOI_MAX) {
            person.path.shadowColor = new paper.Color(0.7, 0.7, 0);
            person.path.shadowBlur = 6;
          } else {
            person.path.shadowColor = new paper.Color(0.2);
            person.path.shadowBlur = 2;
          }
          person.path.shadowOffset = new paper.Point(0, 0);
          //}

          //path.fullySelected = true;
        });
      });

      /**
       *Draws a timeline on at top and at the bottom of the timeline,, from Birthdate of the oldest person to the deathdate of the youngest.
       *
       * @method *drawTime
       * @for Client
       */
      // draw TimeLine
      (function (){
        var year = new Date(Math.ceil(firstBirth.getFullYear()/10) *10, 1,1);

        while (lastDeath.getTime() >= year.getTime()) {
          var x = getX(year);
          var vLine = new paper.Path.Line(new paper.Point(x, 0), new paper.Point(x, y));
          vLine.strokeColor = TIMELINE_COLOR;
          vLine.strokeWidth = 1;
          vLine.sendToBack();

          var textTimeLineStyle = {
            fillColor: TIMELINE_TEXT_COLOR,
            font: FONT,
            fontSize: (LINE_THICKNESS)
          };

          var textTimeLineTop = new paper.PointText(new paper.Point(x+3, 15));
          textTimeLineTop.content = year.getFullYear();
          textTimeLineTop.style = textTimeLineStyle;
          var textTimeLineBottom = new paper.PointText(new paper.Point(x+3, y-5));
          textTimeLineBottom.style = textTimeLineStyle;
          textTimeLineBottom.content = textTimeLineTop.content;

          year.setFullYear(year.getFullYear() + 10);
        }
      })();
      console.log("finished drawing");
    }
    drawEverything();

    canvas.width = WIDTH;
    canvas.height = y;
    /**
     *Sets the clicked LifeLine in focus, starts the line animation, and starts calculation of Dois.
     *
     * @method setFocusLine
     * @param {Path} line The lifeline which is new Focus point.
     * @for Client
     */
    function setFocusLine(line) {
      var person = persons[line.data.id];
      var anim = true;

      resetDois(DOI_MAX + 1);
      /**
       *This recursive function calculates the DOI values for every person, starting at the person in focus.
       *
       * @method setDois
       * @param {Person} p Person in focus
       * @param {Number} currentDoi maximal DOI value
       * @for Client
       */
      function setDois(p, currentDoi) {
        p.childRelationships.forEach(function (relId) {
          var rel = relationships[relId];
          var otherPerson = persons[otherPersonId(p, rel)];
          if (otherPerson.doi === DOI_MAX + 1) {
            otherPerson.doi = currentDoi - DOI_CHILD_RATE;
          } else {
            otherPerson.doi = Math.max(currentDoi - DOI_CHILD_RATE, otherPerson.doi);
          }

          if (currentDoi - DOI_CHILD_RATE > 0) {
            setDois(otherPerson, currentDoi - DOI_CHILD_RATE);
          }
        });
        p.conjugalRelationships.forEach(function (relId) {
          var rel = relationships[relId];
          var otherPerson = persons[otherPersonId(p, rel)];
          if (otherPerson.doi === DOI_MAX + 1) {
            otherPerson.doi = currentDoi - DOI_CONJUGAL_RATE;
          } else {
            otherPerson.doi = Math.max(currentDoi - DOI_CONJUGAL_RATE, otherPerson.doi);
          }

          if (currentDoi - DOI_CONJUGAL_RATE > 0) {
            setDois(otherPerson, currentDoi - DOI_CONJUGAL_RATE);
          }
        });
      }

      person.doi = DOI_MAX;
      setDois(person, DOI_MAX);

      // start animation
      if (!$("#disable_animations_check").prop("checked") && person.block.persons.length > 1 && person.block.persons[0] != person) {
        if (person.path.strokeColor.gradient !== undefined) {
          person.path.strokeColor = person.path.strokeColor.gradient.stops[0].color;
        }
        person.path.strokeColor.alpha = 1;
        person.path.strokeColor = personColor(person);
        person.textName.visible = false;
        person.textDoi.visible = false;
        lineAnim.from = person.path.firstSegment.point.y;
        lineAnim.to = person.block.persons[0].path.firstSegment.point.y;
        lineAnim.path = person.path;
        lineAnim.active = true;
        lineAnim.total = Math.abs(lineAnim.to - lineAnim.from);
        lineAnim.sign = sign(lineAnim.to - lineAnim.from);
        console.log("animation start");
      } else {
        anim = false;
      }

      // push line to the start of the block
      var block = person.block;
      var j = block.persons.indexOf(person);
      block.persons.splice(j, 1);
      block.persons.splice(0, 0, person);
      isDefaultDois = false;

      // redraw if no animation
      if (!anim) {
        drawEverything();
      }
    }
    /**
     * Draws annotation textbox. Calculates textbox position and text breaks.
     *
     * @method drawAnnotation
     * @param {Path} AnnotationSymbol includes Position and AnnotationData
     * @for Client
     */
    function drawAnnotation(annotationSymbol){
      function breakText(item, maxWidth){
        var shortItem = null;
        if (item.bounds.width > maxWidth){
          shortItem = new paper.PointText();
          var string = "";
          var oldString = "";
          shortItem.content = "";
          var content = item.content.split(" ");
          for(var i = 0; i < content.length; i++){
            if(shortItem.bounds.width < maxWidth){
              oldString = string;
              string += content[i] +" ";
              shortItem.content = string;
              if(shortItem.bounds.width > maxWidth){
                string = oldString+"\n"+ content[i] + " ";
              }
              shortItem.content = string;
            }
            shortItem.content = string;
          }
          shortItem.content = "";
          return string;
        }
        else {
          return item.content;
        }
      }
      var padding = 3;
      var fontSize = 11;
      var annoMaxWidth = 90;
      var x = annotationSymbol.data.x +annotationSymbol.bounds.width/2;
      //console.log(annotationSymbol.position.y)
      var y = annotationSymbol.position.y +LINE_THICKNESS;
      var title = annotationSymbol.data.date.toLocaleDateString()  + ":    " + annotationSymbol.data.title;

      var description = annotationSymbol.data.text;
      var annoGroup = new paper.Group();
      var textAnnoStyle = {
        fontSize: fontSize,
        fontFamily: FONT,
        fontColor: "black",
        justification: 'left'

      };

      var titleItem = new paper.PointText(new paper.Point(x,y));
      titleItem.content = title;
      titleItem.style = textAnnoStyle;
      titleItem.fontWeight = "bold";
      titleItem.content = breakText(titleItem,annoMaxWidth);
      var boundingRectWidth = titleItem.bounds.width;
      var boundingRectHeight = titleItem.bounds.height;
      var textItem = null;
      if (description  !== null){
        textItem = new paper.PointText(x, y + boundingRectHeight + fontSize*0.4);
        textItem.content = description;
        textItem.style = textAnnoStyle;
        textItem.content = breakText(textItem,annoMaxWidth);
        boundingRectWidth = Math.max(boundingRectWidth, textItem.bounds.width);
        boundingRectHeight += textItem.bounds.height;

      }
      var boundingRect = new Path.Rectangle(new Point(titleItem.bounds.x - padding-8,titleItem.bounds.y - padding), new Size((boundingRectWidth+8) +2*padding, boundingRectHeight+ 2*padding));
      boundingRect.fillColor = "#ccc";

      boundingRect.opacity = 0.9;
      boundingRect.shadowColor = "black";
      boundingRect.shadowBlur = 3;
      boundingRect.shadowOffset = new paper.Point(3,2);

      annoGroup.addChild(boundingRect);
      annoGroup.addChild(titleItem);
      if(textItem !== null)
        annoGroup.addChild(textItem);

      if(annoGroup.bounds.topRight.x >= WIDTH)
        annoGroup.position.x -= annoGroup.bounds.width;

      if(annoGroup.bounds.bottomRight.y >= canvas.height)
        annoGroup.position.y -= annoGroup.bounds.height;

      annotationSymbol.moveAbove(annoGroup);
    }

    //================================================================================
    // mouse click events
    //================================================================================

    // search
    /**
     * Conducts person search, and sets this person in focus.
     *
     * @method selectMatchingLine
     * @for Client
     */
    function selectMatchingLine() {
      var query = $("#search_input").val();
      var p;

      if (query === null || query === undefined || query === "") {
        return;
      }

      for (var i = 0; i < persons.length; ++i) {
        p = persons[i];
        if (p === null || p === undefined) {
          continue;
        }

        if (p.name.toLowerCase().indexOf(query.toLowerCase()) !== -1) {
          setFocusLine(p.path);
          drawEverything();
          break;
        }
      }
    }
    /**
     * Starts person search on key "enter".
     *
     * @event keypress
     * @for Client
     */
    $("#search_input").keypress(function(e) {
      if(e.which === 13) { // enter
        selectMatchingLine();
      }
    });
    $("#search_btn").click(selectMatchingLine);

    // show-visible checkbox
    /**
     *Displays invisible lines
     *
     * @event show_invisible_check
     * @for Client
     */
    $("#show_invisible_check").change(function () {
      drawEverything();
    });

    // mouse clicks in canvas
    /**
     *  Starts different interactions, depending on which object was clicked.
     *
     * @event onMouseDown
     * @for Client
     */
    paper.install(window);
    var tool = new paper.Tool();
    tool.activate();

    tool.onMouseDown = function (event) {
      console.log("click");
      var hitOptions = {
        segments: true,
        stroke: true,
        fill: true,
        tolerance: 2
      };
      var hitResult = paper.project.hitTest(event.point, hitOptions);
      if (hitResult) {
        // we have a hit, do something here
        if( hitResult.item.data instanceof EventAnnotation){
          drawEverything();
          if (hitResult.item.fillColor.alpha === 1)
            drawAnnotation(hitResult.item);
        }else{
          if($.isEmptyObject(hitResult.item.data)){
            console.log("nothing happening");
          }else{
            setFocusLine(hitResult.item);
            //drawEverything();
          }
        }
      } else {
        resetDois(DOI_MAX);
        sortBlockPersons();
        isDefaultDois = true;
        drawEverything();
      }


    }

    // animations
    /**
     * If animation Event takes place, animate LifeLine
     *
     * @event onFrame Animation
     * @for Client
     */
    view.onFrame = function (event) {
      var s;
      var dy;
      var remaining;
      var total;

      if (lineAnim.active) {
        remaining = Math.abs(lineAnim.path.firstSegment.point.y - lineAnim.to);
        dy = LINE_ANIM_SPEED * event.delta;
        dy = lineAnim.total * 0.02 + dy * (remaining / lineAnim.total);
        lineAnim.path.translate(new Point(0, lineAnim.sign * Math.min(dy, remaining)));
        if (Math.abs(lineAnim.path.firstSegment.point.y - lineAnim.to) <= 0.01) {
          lineAnim.active = false;
          console.log("animation end");
          drawEverything();
        }
      }
    };
    //on window Resize
    /**
     * If window changes size resize and redraw TimeNets
     *
     * @event onresize
     * @for Client
     */
    $(window).on('resize', function (e) {
      WIDTH = Math.floor($(window).width() * 0.9);
      canvas.width = WIDTH;
      drawEverything();
      canvas.height = y;
    });
  });

  $("#request").click(function () {
    var id = $("#combo_timenets").val();
    socket.emit("get_data", {id: id});
  });

});
