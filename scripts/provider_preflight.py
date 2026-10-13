"""Check account model access without sending CV/posting content or making a generation."""
from portal import providers
try:
    result=providers.preflight()
    print('Account model available:',result['model'])
    print('Atlas monthly limit: $'+str(result['monthly_budget_usd']))
    print('No profile data sent; writing quality and token usage require a separate consented generation.')
except ValueError as e:raise SystemExit(str(e))
except Exception as e:raise SystemExit('Provider connectivity check failed: '+type(e).__name__)
