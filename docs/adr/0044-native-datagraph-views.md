# ADR 0044: Native DataGraph views and runner ownership

Status: Accepted

Extend ADR 0040 to recognize the actual rdflib-turbo Graph and StoreDataset
classes. A marker attribute alone does not authorize foreign native stores.
Wrappers retain the same owner and exact selected scope. Independent clones
use the provider's native scoped copy, preserving contexts and empty domains;
they must not serialize the base into RDFLib or construct a second interpreter.

Public runners dispatch through the existing borrowed validation and rule
protocol on the underlying native graph. Native inference preparation must
retain that owner instead of taking the ordinary RDF transport path. Ordinary
RDFLib views retain their existing behavior. Unsupported native clone renaming
fails explicitly until the provider exposes an exact scoped rename operation.
