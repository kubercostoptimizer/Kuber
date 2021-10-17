function bo(numCoupledConstraints)
        cpu = optimizableVariable('cpu',{'2' '4' '8' '16'},'Type','categorical');
        speed = optimizableVariable('speed',{'slow' 'fast'},'Type','categorical');
        ram = optimizableVariable('ram',{'low' 'medium' 'high'},'Type','categorical');

        %Initalvaluesc = [-1 -1 -1 -1 -1 -1 -1 -1 -1 -1]
        %'InitialConstraintViolations',Initalvaluesc, ... 
        
        Initalvaluesx = cell2table({categorical({'2'}) categorical({'slow'}) categorical({'medium'})})%readtable('VMtypes_to_propagate.csv');
        %'InitialX', Initalvaluesx, ...

        obj = @func;
        results = bayesopt(obj, [cpu, speed, ram], 'IsObjectiveDeterministic', true, ...
                'AcquisitionFunctionName', 'expected-improvement-plus', ...
                'Verbose', 2, ...
                'UseParallel',true, ...
                'PlotFcn', [], ...
                'MaxObjectiveEvaluations',10, ...
                'OutputFcn', @outputfun, ...
                'NumCoupledConstraints', numCoupledConstraints, ...
                'XConstraintFcn', @xconstraint);

        function [tf] = xconstraint(in)
                speed = in.speed;
                ram = in.ram;
                tf = ((speed == 'slow' & ram ~= 'low') | (speed == 'fast' & ram == 'low'));
        end

        function stop = outputfun(results,state)
                stop = false;
                switch state
                    case 'iteration'
                        current_best = results.MinObjective;
                        next_best = predictObjective(results,results.NextPoint);
                        diff_best = (abs(current_best-next_best))/current_best;
                        if diff_best <= 0.10
                             stop = true
                        end
                end
        end

        function [fval, cons] = func(in)
                cpu = char(in.cpu);
                speed = char(in.speed);
                ram = char(in.ram);
                pathToCostFunc = fileparts('/wd/code/kuber/BO_Matlab/cost_function.py');
                if count(py.sys.path,pathToCostFunc) == 0
                        insert(py.sys.path,int32(0),pathToCostFunc);
                end
                pyout = py.cost_function.evaluate(cpu, speed, ram);
                fval = pyout{1};
                cons = cellfun(@double,cell(pyout{2}));
        end
end