-- Get geographic information of all active field boundaries for real customers
-- Pull bounding boxes if present, otherwise pull full boundary
select top 1000 fb.FieldId, CASE WHEN fdb.BoundingRegion IS NULL THEN 0 ELSE 1 END as IsBoundingBox, ISNULL(fdb.BoundingRegion, fb.BoundingPolygon).STAsText() as PolygonWKT from FieldBoundaries fb
LEFT JOIN FieldDataBounds fdb ON (fb.FieldId = fdb.FieldId)
INNER JOIN [dbo].[GetValidAccountIds](1) a ON (fb.[AccountId] = a.[AccountId])
where fb.IsActiveFieldBoundary = 1
order by a.AccountId, fb.FieldId
;