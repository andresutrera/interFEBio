Mesh.MshFileVersion = 2.2;
p1 = newp; Point(p1) = {0,0,0};
p2 = newp; Point(p2) = {1,0,0};
p3 = newp; Point(p3) = {1,1,0};
p4 = newp; Point(p4) = {0,1,0};


c1 = newp; Point(c1) = {0,0,1.05};
c2 = newp; Point(c2) = {1.5,0,1.05};
c3 = newp; Point(c3) = {1.5,1.5,1.05};
c4 = newp; Point(c4) = {0,1.5,1.05};

l1 = newl; Line(l1) = {p1,p2};
l2 = newl; Line(l2) = {p2,p3};
l3 = newl; Line(l3) = {p3,p4};
l4 = newl; Line(l4) = {p4,p1};

cl1 = newl; Line(cl1) = {c1,c2};
cl2 = newl; Line(cl2) = {c2,c3};
cl3 = newl; Line(cl3) = {c3,c4};
cl4 = newl; Line(cl4) = {c4,c1};

ll = newll; Line Loop(ll) = {l1,l2,l3,l4};
s01 = news; Surface(s01) = {ll};

cll = newll; Line Loop(cll) = {cl4,cl3,cl2,cl1};
cs01 = news; Surface(cs01) = {-cll};

Transfinite Line {l1,l2,-l3,-l4} = 5;
Transfinite Surface {s01};
Recombine Surface {s01};

Transfinite Line {cl1,cl2,-cl3,-cl4} = 5;
Transfinite Surface {cs01};
Recombine Surface {cs01};

Extrude {0,0,1} {
Surface{s01}; Layers{4}; Recombine;}

Physical Volume("Solid") = {1};
Physical Surface("xsym") = {33};
Physical Surface("ysym") = {21};
Physical Surface("zsym") = {10};
Physical Surface("top") = {34};
Physical Surface("contact") = {12};
