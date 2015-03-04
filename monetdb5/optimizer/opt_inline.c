/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0.  If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 *
 * Copyright 2008-2015 MonetDB B.V.
 */

#include "monetdb_config.h"
#include "opt_inline.h"

extern int OPTinlineMultiplex(Client cntxt, MalBlkPtr mb, InstrPtr p);

static int
isCorrectInline(MalBlkPtr mb){
	/* make sure we have a simple inline function with a singe return */
	InstrPtr p;
	int i, retseen=0;

	for( i= 1; i < mb->stop; i++){
		p= getInstrPtr(mb,i);
		if ( p->token == RETURNsymbol || p->token == YIELDsymbol || 
			 p->barrier == RETURNsymbol || p->barrier == YIELDsymbol)
			retseen++;
	}
	return retseen <= 1;
}


int
OPTinlineImplementation(Client cntxt, MalBlkPtr mb, MalStkPtr stk, InstrPtr p)
{
	int i;
	InstrPtr q,sig;
	int actions = 0;

	(void) p;
	(void)stk;

	for (i = 1; i < mb->stop; i++) {
		q = getInstrPtr(mb, i);
		if( q->blk ){
			sig = getInstrPtr(q->blk,0);
			/*
			 * Time for inlining functions that are used in multiplex operations.
			 * They are produced by SQL compiler.
			 */
			if( getFunctionId(q)== multiplexRef &&
				getModuleId(q) == malRef &&
				OPTinlineMultiplex(cntxt,mb,q)){

				OPTDEBUGinline {
					mnstr_printf(cntxt->fdout,"#multiplex inline function\n");
					printInstruction(cntxt->fdout,mb,0,q,LIST_MAL_ALL);
				}

			    varSetProp(mb, getArg(q,0), inlineProp, op_eq, NULL);
			} else
			/*
			 * Check if the function definition is tagged as being inlined.
			 */
			if (sig->token == FUNCTIONsymbol &&
			    varGetProp(q->blk, getArg(sig, 0), inlineProp) != NULL &&
				isCorrectInline(q->blk) ) {
				(void) inlineMALblock(mb,i,q->blk);
				i--;
				actions++;
				OPTDEBUGinline {
					mnstr_printf(cntxt->fdout,"#inline function at %d\n",i);
					printFunction(cntxt->fdout, mb, 0, LIST_MAL_ALL);
					printInstruction(cntxt->fdout,q->blk,0,sig,LIST_MAL_ALL);
				}
			} else 
			/*
			 * Check if the local call is tagged as being inlined.
			 */
			if (varGetProp(mb, getArg(q,0), inlineProp) != NULL) {
				inlineMALblock(mb,i,q->blk);
				i--;
				actions++;
				OPTDEBUGinline {
					mnstr_printf(cntxt->fdout,"#inlined called at %d\n",i);
					printFunction(cntxt->fdout, mb, 0, LIST_MAL_ALL);
					printInstruction(cntxt->fdout,q->blk,0,sig,LIST_MAL_ALL);
				}
			} 
		}
	}
	return actions;
}


int OPTinlineMultiplex(Client cntxt, MalBlkPtr mb, InstrPtr p){
	Symbol s;
	str mod,fcn;
	int res;

	mod = VALget(&getVar(mb, getArg(p, 1))->value);
	fcn = VALget(&getVar(mb, getArg(p, 2))->value);
	if( (s= findSymbol(cntxt->nspace, mod,fcn)) ==0 )
		return FALSE;
	/*
	 * Before we decide to propagate the inline request
	 * to the multiplex operation, we check some basic properties
	 * of the target function. Moreover, we apply the inline optimizer
	 * to the target function as well.
	 * This code should be protected against overflow due to recursive calls.
	 * In general, this is a hard problem. For now, we just expand.
	 */
	(void) OPTinlineImplementation(cntxt, s->def, NULL, p);
	res= varGetProp(s->def , getArg(getInstrPtr(s->def,0), 0),
				inlineProp) != NULL;
	return res;
}
